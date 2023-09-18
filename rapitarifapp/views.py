from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests

# Create your views here.
API_BASE_URL = "http://192.168.88.129:8012"
#API_BASE_URL = "http://127.0.0.1:8001"

def authentication():
    api_url = f'{API_BASE_URL}/login'
    data_to_send = {
        'username': 'fetra',
        'password': 'fetra',
        # Add more parameters as needed
    }
    response = requests.post(api_url, json=data_to_send)
    if response.status_code == 200:
        data = response.json()  # Assuming the API response is in JSON format
    else:
        # Handle the error, e.g., raise an exception or return an error response
        #print(f"Error: {response.status_code}")
        data = None
    
    return data


def index(request):
    auth = authentication()
    if auth != None:
        try:
            api_url = f'{API_BASE_URL}/api/bureaux'
            jwt_token = auth['access']
            headers = {
                'Authorization': f'Bearer {jwt_token}'
            }
            response2 = requests.get(api_url, headers=headers)
            if response2.status_code == 200:
                # The request was successful
                response_data2 = response2.json()
            else:
                # Handle the error, e.g., raise an exception or return an error response
                #print(f"Error: {response2.status_code}")
                response_data2 = None
                raise Exception(f"Désolé, impossible de charger les bureux. Code: {response.status_code}")
        except Exception as e:
            error_message = str(e)

            # Log the error for debugging (you can use Python's logging module)
            import logging
            logging.error(error_message)            
    else:
        # Handle the error, e.g., raise an exception or return an error response
        #print(f"Error: {response.status_code}")
        data = None

    if request.method == 'POST':
        #print(request.POST)
        bureauDepart = request.POST.get('codeDepart').split("-")[1]
        depart = request.POST.get('codeDepart').split("-")[0] 
        bureauArrive = request.POST.get('codeArrive').split("-")[1]
        arrive = request.POST.get('codeArrive').split("-")[0] 
        poids = request.POST.get('pds')
        longueur = request.POST.get('long')
        larg = request.POST.get('larg')
        haut = request.POST.get('haut')

        longueur=0 if longueur=='' else float(longueur)
        larg=0 if larg=='' else float(larg)
        haut=0 if haut=='' else float(haut)
        
        pr = poids
        pv = longueur*larg*haut/5000
        if float(poids) < pv:
            poids = pv

        #print(pv)
        error_message = None
        auth = authentication()
        if auth != None:
            try:   
                api_url = f'{API_BASE_URL}/api/zone/{depart}/{arrive}'
                jwt_token = auth['access']
                headers = {
                    'Authorization': f'Bearer {jwt_token}'
                }
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    # The request was successful
                    response_data = response.json()
                    datazone = response_data #for memory
                    zone=response_data[0]['zonemodifier']
                    try:
                        api_url = f'{API_BASE_URL}/api/tarifs/{zone}/{poids}'
                        response = requests.get(api_url, headers=headers)
                        if response.status_code == 200:
                            response_data = response.json()
                        else:
                            raise Exception(f"Désolé, erreur de la génération de la tarif. Code: {response.status_code}")
                    except Exception as e:
                        error_message = str(e)
                else:
                    # Handle the error, e.g., raise an exception or return an error response
                    print(f"Error: {response.status_code}")
                    response_data = None
                    raise Exception(f"Désolé, zone inconnue. Code: {response.status_code}")
            except Exception as e:
                error_message = str(e)

                # Log the error for debugging (you can use Python's logging module)
                import logging
                logging.error(error_message)
        #print(response_data)
        context = {
            'poidsreel': pr,
            'poidsvol': pv,
            'poids': poids,
            'datazone': datazone,
            'data': response_data,
            'message': error_message,
            'bureaux': response_data2,
            'bureaux_requested': f"{bureauDepart} {depart} à {bureauArrive} {arrive}",
        }
        return render(request, 'index.html', context)
    else:
        context = {
            'author': 'fetra',
            'bureaux': response_data2,
        }
        return render(request, 'index.html', context)
