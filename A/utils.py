from kavenegar import * 


def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('56712F704A59496B50762B4B38656D5950386975536C53754F776E6A367554514172345239636B495375413D')
        params = {
            'sender': '',
            'receptor': 'phone_number',
            'message': f'{code} کد تایید شما'
        }
        response = api.sms_send(params)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


