from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
# from verify_email.email_handler import send_verification_email
# from django.conf.core import send_mail
import requests
import json


# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    # return render(request, "voting/login.html", context)


def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    # return None
    for position in positions:
        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            if position.max_vote > 1:
                instruction = "You may select up to " + \
                              str(position.max_vote) + " candidates"
                input_box = '<input type="checkbox" value="' + str(candidate.id) + '" class="flat-red ' + \
                            position_name + '" name="' + \
                            position_name + "[]" + '">'
            else:
                instruction = "Select only one candidate"
                input_box = '<input value="' + str(candidate.id) + '" type="radio" class="flat-red ' + \
                            position_name + '" name="' + position_name + '">'
            image = "/media/" + str(candidate.photo)
            candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="' + candidate.fullname + '" data-bio="' + candidate.bio + '"><i class="fa fa-search"></i> Platform</button><img src="' + \
                              image + '" height="100px" width="100px" class="clist"><span class="cname clist">' + \
                              candidate.fullname + '</span></li>'
        up = ''
        if position.priority == 1:
            up = 'disabled'
        down = ''
        if position.priority == positions.count():
            down = 'disabled'
        output = output + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""

        if display_controls:
            output = output + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
        </div>"""

        output = output + f"""</div>
        <div class="box-body">
        <p>{instruction}
        <span class="pull-right">
        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
        </span>
        </p>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ''
    return output


def fetch_ballot(request):
    output = generate_ballot(display_controls=True)
    return JsonResponse(output, safe=False)


def generate_otp(request):
    """Link to this function to generate random numbers with python
    https://www.codespeedy.com/otp-generation-using-random-module-in-python/
    """
    import random as r

    otp = ""
    for i in range(r.randint(5, 8)):
        otp += str(r.randint(1, 9))
    return otp

    #Generate random numbers mix with alphabets
    # import random as r
    # import string

    # # Function to generate a mixed OTP with a given length
    # def generate_mixed_otp(length):
    #     characters = string.ascii_uppercase + string.digits  # Combine uppercase alphabets and digits
    #     otp = ''.join(r.choice(characters) for _ in range(length))  # Randomly choose characters and join them
    #     return otp

    # # Generate a random length for the OTP between 5 and 8 characters
    # otp_length = r.randint(5, 8)

    # # Call the function to generate the mixed OTP
    # otp = generate_mixed_otp(otp_length)

    # # Print the generated OTP
    # print(otp)

    # request.session['code'] = otp
    # send_mail("This is your OTP to vote ",otp,"adediranadedamolagoodness@gmail.com",[request.session['email']], fail_silently=False)
    # return render(request, "voting/voter/verify.html")


def dashboard(request):
    user = request.user
    # * Check if this voter has been verified
    if user.voter.otp is None or user.voter.verified == False:
        if not settings.SEND_OTP:
            # Bypass
            msg = bypass_otp()
            messages.success(request, msg)
            return redirect(reverse('show_ballot'))
        else:
            return redirect(reverse('voterVerify'))
    else:
        if user.voter.voted:  # * User has voted
            # To display election result or candidates I voted for ?
            context = {
                'my_votes': Votes.objects.filter(voter=user.voter),
            }
            return render(request, "voting/voter/result.html", context)
        else:
            return redirect(reverse('show_ballot'))


def otp_ver(request):
    if request.method == 'POST':
        otp_ = request.POST.get("code")
    if otp_ == request.session["code"]:
        encryptedpassword = make_password(request.session['password'])
        nameuser = User(username=request.session['username'], email=request.session['email'],
                        password=encryptedpassword)
        nameuser.save()
        messages.info(request, 'signed in successful...')
        User.is_active = True
        return render(request, "voting/voter/ballot.html")
    else:
        messages.error(request, 'otp not correct')
        return render(request, "voting/voter/verify.html")


def verify(request):
    context = {
        'page_title': 'OTP Verification'
    }
    return render(request, "voting/voter/verify.html", context)


def register_user(request):
    if form.is_valid():
        inactive_user = send_verification_email(request, form)


def resend_otp(request):
    user = request.user
    voter = user.voter
    error = False
    if settings.SEND_OTP:
        if voter.otp_sent >= 3:
            error = True
            response = "You have requested OTP three times. You cannot do this again! Please enter previously sent OTP"
        else:
            email = voter.admin.email
            # Now, check if an OTP has been generated previously for this voter
            # otp = voter.otp
            # if otp is None:
            # Generate new OTP
            otp = generate_otp(request)
            voter.otp = otp
            voter.save()
            try:
                # writeup = "Dear " + str(user) + ", Kindly use " + str(otp) + " as your voting OTP, kindly keep it safe as it can only be used by you alone."
                msg = str(otp)
                message_is_sent = send_sms(email, msg)
                if message_is_sent:  # * OTP was sent successfully
                    # Update how many OTP has been sent to this voter
                    # Limited to Three so voters don't exhaust OTP balance
                    voter.otp_sent = voter.otp_sent + 1
                    voter.save()

                    response = "OTP has been sent to your phone number. Please provide it in the box provided below. Kindly know that any delay experienced is caused by your service provider"
                else:
                    error = False
                    response = "OTP has been sent to your email. Please provide it in the box provided below. Kindly know that any delay experienced is caused by your service provider"
            except Exception as e:
                response = "OTP could not be sent." + str(e)

                # * Send OTP
    else:
        # ! Update all Voters record and set OTP to 0000
        # ! Bypass OTP verification by updating verified to 1
        # ! Redirect voters to ballot page
        response = bypass_otp()
    return JsonResponse({"data": response, "error": error})


def bypass_otp():
    Voter.objects.all().filter(otp=None, verified=False).update(otp="0000", verified=True)
    response = "Kindly cast your vote"
    return response


def send_sms(phone_number, msg):
    """Read More for SMS OTP
    https://www.multitexter.com/developers
    """
    # import requests
    # import os
    # import json
    # response = ""
    # user = request.user
    # voter = user.voter

    # import random as r
    #
    # otp = ""
    # for i in range(r.randint(5, 8)):
    #     otp += str(r.randint(1, 9))

    # otp.save()

    # used termii API for email OTP generation

    url = "https://api.ng.termii.com/api/email/otp/send"

    print("==== content is", msg)
    print("====== " + phone_number)

    payload = {
        "api_key": "TLoB0LVhTHj6p05EBDmCE1zR9zQA7y3SxyZWgdPoRKfEmXrsitxtAJFZe5u1bf",
        "email_address": phone_number,
        "code": msg,
        "email_configuration_id": "1df5f9ea-6bfb-49c9-9de1-cfcafb4abb98"
    }

    header = {
        "Content-Type": "application/json"
    }
    print("==== Sending Otp")
    response = requests.post(url=url, headers=header, json=payload)

    print(response.text)

    # email = os.environ.get('SMS_EMAIL')
    # password = os.environ.get('SMS_PASSWORD')
    # if email is None or password is None:
    # raise Exception("Email/Password cannot be Null")

    # SMS otp API
    url = "https://app.multitexter.com/v2/app/sms"
    data = {"email": 'adediranadedamolagoodness@gmail.com', "password": 'OluwafemisolA.22', "message": msg,
            "sender_name": "FUNIEC", "recipients": phone_number, "forcednd": 1}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain',
               'Authorization': 'Bearer {4OdamR3cbMB3G1yQrm4eNkElHLNro5xkB82tI2pXgXkfIUVp27t9cuq2bdnS}'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    response = r.json()
    status = response.get('status', 0)
    if str(status) == '1':
        return True
    else:
        return False


def verify_otp(request):
    error = True
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    else:
        otp = request.POST.get('otp')
        if otp is None:
            messages.error(request, "Please provide valid OTP")
        else:
            # Get User OTP
            voter = request.user.voter
            db_otp = voter.otp
            if db_otp != otp:
                messages.error(request, "Provided OTP is not valid")
            else:
                messages.success(
                    request, "You are now verified. Please cast your vote")
                voter.verified = True
                voter.save()
                error = False
    if error:
        return redirect(reverse('voterVerify'))
    return redirect(reverse('show_ballot'))


def show_ballot(request):
    if request.user.voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))
    ballot = generate_ballot(display_controls=False)
    context = {
        'ballot': ballot
    }
    return render(request, "voting/voter/ballot.html", context)


def preview_vote(request):
    if request.method != 'POST':
        error = True
        response = "Please browse the system properly"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id
            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                if len(form_position) > max_vote:
                    error = True
                    response = "You can only choose " + \
                               str(max_vote) + " candidates for " + position.name
                else:
                    # for key, value in form.items():
                    start_tag = f"""
                       <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>
                                
                    
                    """
                    end_tag = "</ul></span></div><hr/>"
                    data = ""
                    for form_candidate_id in form_position:
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position)
                            data += f"""
		                      	<li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                            """
                        except:
                            error = True
                            response = "Please, browse the system properly"
                    output += start_tag + data + end_tag
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                # Max Vote == 1
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
		                    </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Please, browse the system properly"
    context = {
        'error': error,
        'list': output
    }
    return JsonResponse(context, safe=False)


def submit_ballot(request):
    if request.method != 'POST':
        messages.error(request, "Please, browse the system properly")
        return redirect(reverse('show_ballot'))

    # Verify if the voter has voted or not
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
    form.pop('submit_vote', None)  # Pop Submit Button

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Please select at least one candidate")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.all()
    form_count = 0
    for position in positions:
        max_vote = position.max_vote
        pos = slugify(position.name)
        pos_id = position.id
        if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            if form_position is None:
                continue
            if len(form_position) > max_vote:
                messages.error(request, "You can only choose " +
                               str(max_vote) + " candidates for " + position.name)
                return redirect(reverse('show_ballot'))
            else:
                for form_candidate_id in form_position:
                    form_count += 1
                    try:
                        candidate = Candidate.objects.get(
                            id=form_candidate_id, position=position)
                        vote = Votes()
                        vote.candidate = candidate
                        vote.voter = voter
                        vote.position = position
                        vote.save()
                    except Exception as e:
                        messages.error(
                            request, "Please, browse the system properly " + str(e))
                        return redirect(reverse('show_ballot'))
        else:
            this_key = pos
            form_position = form.get(this_key)
            if form_position is None:
                continue
            # Max Vote == 1
            form_count += 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(
                    position=position, id=form_position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                vote.save()
            except Exception as e:
                messages.error(
                    request, "Please, browse the system properly " + str(e))
                return redirect(reverse('show_ballot'))
    # Count total number of records inserted
    # Check it viz-a-viz form_count
    inserted_votes = Votes.objects.filter(voter=voter)
    if (inserted_votes.count() != form_count):
        # Delete
        inserted_votes.delete()
        messages.error(request, "Please try voting again!")
        return redirect(reverse('show_ballot'))
    else:
        # Update Voter profile to voted
        voter.voted = True
        voter.save()
        messages.success(request, "Thanks for voting")
        return redirect(reverse('voterDashboard'))



# Here's a breakdown of the main functions and their purposes:

# index(request): This function checks if a user is authenticated and returns a login page if not. However, it seems to be commented out.

# generate_ballot(display_controls=False): This function generates the ballot for voting. It fetches positions and candidates, creates input elements (checkboxes or radio buttons) for each candidate, and generates HTML for the ballot. The display_controls parameter is used to include control buttons for reordering positions.

# fetch_ballot(request): This view returns the generated ballot as JSON.

# generate_otp(request): Generates a random OTP (One-Time Password) for voter verification. It's currently commented out.

# dashboard(request): Checks if a voter is verified and whether they've voted. It redirects voters accordingly.

# otp_ver(request): Handles OTP verification for voters.

# verify(request): Renders the OTP verification page.

# register_user(request): This function seems incomplete and lacks a form definition.

# resend_otp(request): Resends OTP to voters for verification.

# bypass_otp(): Bypasses OTP verification for voters and sets their OTP to "0000." It's used in cases where OTP is not being sent.

# send_sms(phone_number, msg): Sends an SMS OTP. It seems to be using an external API for sending SMS.

# verify_otp(request): Verifies OTP entered by the voter.

# show_ballot(request): Renders the page to display the ballot.

# preview_vote(request): Handles the preview of selected candidates before submitting the vote.

# submit_ballot(request): Records the vote when the voter submits their choices.
