import requests
import xmltodict
import json

xml_url = "https://smstestbed.nist.gov/vds/Mazak01/sample"

def extract_and_consolidate_events(data):
    event_data = []  # To store consolidated event data
 
    # Traverse the dictionary to find event data
    for component in data.get("MTConnectStreams", {}).get("DeviceStream", []).get("ComponentStream"):
        for category, details in component.items():
            if "Events" in details:
                events = details["Events"]
                for event_type, event_list in events.items():
                    if isinstance(event_list, list):
                        for event in event_list:
                            event_data.append(event)
 
    return event_data

try:
    # Fetch XML data from the URL
    response = requests.get(xml_url)

    if response.status_code == 200:
        # Parse XML data and convert it to a dictionary
        data_dict = xmltodict.parse(response.text)

        # Convert the dictionary to JSON
        json_data = json.dumps(data_dict, indent=4)

        # Print or use the JSON data
        #print(json_data)

        json_dict = json.loads(json_data)

        # device_name = json_dict.get("MTConnectStreams", {}).get("Streams", {}).get("DeviceStream", {}).get("ComponentStream")
        
        # if device_name:
        #     print("Device Name:", device_name)
        # mazak01_b_samples = json_dict["MTConnectStreams"]["Streams"]["DeviceStream"]["ComponentStream"][0]

        # # Extract Samples data for "Mazak01-C"
        # mazak01_c_samples = json_dict["MTConnectStreams"]["Streams"]["DeviceStream"]["ComponentStream"][1]["Samples"]

        # Print the Samples data for "Mazak01-B"
        # print("Samples data for Mazak01-B:")
        # print(json.dumps(mazak01_b_samples, indent=2))

        # # Print the Samples data for "Mazak01-C"
        # print("Samples data for Mazak01-C:")
        # print(json.dumps(mazak01_c_samples, indent=2))
        event_data = extract_and_consolidate_events(json_dict)  
        print(event_data)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except xmltodict.expat.ExpatError as e:
    print(f"XML parsing error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
