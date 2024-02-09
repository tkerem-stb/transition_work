from datetime import date, datetime, timedelta

from shared.extractors import ApiDataExtractor
from shared.azure import get_configuration_vault_secret, get_azure_sql_connection, upload_blob_from_stream

import logging
import pyodbc
import xml.etree.ElementTree as et
import dateutil.parser as dup

from abc import ABC
import requests
import base64

# class WorkdayCensusApiPipeline (ABC) :

def _basic_header(username: str, password: str ) -> str:
  token = base64.urlsafe_b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
  return f'Basic {token}'

def _get_auth_headers () -> dict:
  client_id = get_configuration_vault_secret( secret_name='PipelinesWorkdayClientId' )
  client_secret = get_configuration_vault_secret( 'PipelinesWorkdayClientSecret' )
  refresh_token = get_configuration_vault_secret( 'PipelinesWorkdayRefreshToken' )
  token_url = get_configuration_vault_secret( 'PipelinesWorkdayTokenUrl' )

#   print(f'Client_ID: {client_id}')
#   print(f'client_secret: {client_secret}')
#   print(f'refresh_token: {refresh_token}')
#   print(f'token_url: {token_url}')


  auth_params = { 
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
  }

  headers = requests.post( url=token_url, headers={ 'Authorization': _basic_header( client_id, client_secret ) }, data=auth_params )
#   print('Headers:',headers.json())
  try :
    token = headers.json()['access_token']
    # print(token)
    #return { 'Authorization': f'Bearer {token}' }
    return token
  except KeyError as k :
    logging.critical( f'No access token found in response {headers} {headers.content}' )
    raise RuntimeError( 'Could not authenticate to Workday' )

def make_soap_request(url, token, soap_payload):
    
    headers = {
        # 'Content-Type': 'text/xml; charset=utf-8',
        'Authorization': f'Bearer {token}'
    }
    # print(headers)
    response = requests.post(url, data=soap_payload, headers=headers)
    if response.status_code == 200:
        return response.content#.decode('utf-8')
    else:
        raise Exception(f"SOAP Request failed: {response.status_code} {response.text}")


# _get_auth_headers () 

# SOAP request URL and payload
soap_url =  'https://wd2-impl-services1.workday.com/ccx/service/stblaw/Talent/v41.0'                 
# soap_payload = """<?xml version="1.0" encoding="UTF-8"?>
#             <env:Envelope
#                 xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
#                 xmlns:xsd="http://www.w3.org/2001/XMLSchema">
#                 <env:Body>
#                     <wd:Get_Schools_Request xmlns:wd="urn:com.workday/bsvc" wd:version="v41.0">
#                         <wd:Response_Filter>
#                             <wd:Page>1</wd:Page>
#                             <wd:Count>100</wd:Count>
#                         </wd:Response_Filter>
#                         <wd:Response_Group>
#                             <wd:Include_Reference>true</wd:Include_Reference>
#                         </wd:Response_Group>
#                     </wd:Get_Schools_Request>
#                 </env:Body>
#             </env:Envelope>"""


soap_payload = """<?xml version="1.0" encoding="utf-8"?>
<env:Envelope
    xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <env:Body>
        <wd:Get_Degrees_Request xmlns:wd="urn:com.workday/bsvc" wd:version="v41.0">
            <wd:Response_Filter>
                <wd:Page>1</wd:Page>
                <wd:Count>100</wd:Count>
            </wd:Response_Filter>
        </wd:Get_Degrees_Request>
    </env:Body>
</env:Envelope>"""


# Execute the functions
try:
    # token = get_bearer_token(auth_url, client_id, client_secret)
    # print(token)
    token = _get_auth_headers () 
  
    # print(token)
    response = make_soap_request(soap_url, token, soap_payload)
    print(response)
    # if 'content-type' in response.headers : content_type = response.headers['content-type'].lower()
    # print(content_type)
except Exception as e:
    print(e)




# # Parse XML response
# root = et.fromstring(response)

# # Create a new XML element for ns0:Report_Entry
# ns_uri = '{urn:com.workday/bsvc}'

# report_entry = et.Element(f"{{ {ns_uri} }}Report_Entry")

# # Append the original XML response to the new ns0:Report_Entry element
# for child in root.findall('.//'):
#     report_entry.append(child)

# new_xml_str = et.tostring(report_entry, encoding = 'utf-8',method ='xml').decode('utf-8')
# print(new_xml_str)
