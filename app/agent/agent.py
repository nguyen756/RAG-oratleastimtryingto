import requests
from vector_engine import Embedder
engine=Embedder()
def check_status(url: str):
    if not url.startswith("https://"):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return True
        else:
            print(f"Received status code {response.status_code} from {url}")
            return False
    except requests.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return False
def calculate_mscs(aspd:int=0, cspd:int=0):
    string_result = []
    if aspd>0:
        ms = 0
        aspd_note = "auto attack speed"
        if aspd >=1100:
            aspd_note = "attack intervals removed"
        if aspd >= 1000:
            ms = min((aspd - 1000) / 180.0, 50.0)
        string_result.append(f"For your {aspd} ASPD: {aspd_note} You get a {ms:.2f}% motion speed boost.")
    if cspd > 0:
        cast_boost = 0.0
        cspd_note = "Normal cast time."
        if cspd >= 10000:
            cspd_note = "cast time removed"
        elif cspd >= 1000:
            cspd_note = "cast time removed by half and plus cast time reduction boost"
            cast_boost = (cspd - 1000) / 180.0
        string_result.append(f"For your {cspd} CSPD: {cspd_note} You get a {cast_boost:.2f}% cast time reduction boost.")

    if not string_result:
        return "No valid speed stats were provided to calculate."
    return "\n".join(string_result)
def general_question(search_query:str):
    results = engine.search(search_query)
    return str(results)

if __name__ == "__main__":
    url = "google.com"
    if check_status(url):
        print("Server is up and running!")
    else:
        print("Server is not responding. Please check the logs for more details.")

    print( calculate_mscs(aspd=9000, cspd=9500))
