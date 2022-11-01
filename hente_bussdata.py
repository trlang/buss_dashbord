import requests
import pandas as pd

def hente_bussdata():
    headers = {"ET-Client-Name": "Munthes"}
    def run_query(query):
        request = requests.post('https://api.entur.io/journey-planner/v3/graphql', json={'query': query}, headers=headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Feilkode {}. {}".format(request.status_code, query))
    query = """
    {
      stopPlaces(ids: ["NSR:StopPlace:4527" "NSR:StopPlace:4531"]){
        id
        name
        estimatedCalls(timeRange: 72100, numberOfDepartures: 2) {
          realtime
          aimedDepartureTime
          expectedDepartureTime
          destinationDisplay {
            frontText
          }
          quay {
            id
          }
          serviceJourney {
            journeyPattern {
              line {
                id
    	    publicCode
                name
              }
            }
          }
        }
      }
    }
    """
            # stopPlaces(ids: ["NSR:StopPlace:4527" "NSR:StopPlace:4531"])
    result = run_query(query)
    def getProps (estimatedCall):
        return {
            'linje': estimatedCall['serviceJourney']['journeyPattern']['line']['publicCode'],
            'destinasjon': estimatedCall['destinationDisplay']['frontText'],
            'sanntid': estimatedCall['expectedDepartureTime'],
            'avgang': estimatedCall['aimedDepartureTime']
                }
    filteredDataList = []
    for i in range(0,2):
        for estimatedCall in result['data']['stopPlaces'][i]['estimatedCalls']:
            filteredDataList.append(getProps(estimatedCall))
    df = pd.DataFrame.from_dict(filteredDataList)
    df['sanntid'] = df['sanntid'].str.slice(11, 19)
    df['avgang'] = df['avgang'].str.slice(11, 19)
    df.sort_values('sanntid', ascending=True, inplace=True)

    return df