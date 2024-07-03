import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def authenticate_google_sheets(credentials_json):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Load credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
    
    # Authorize the client
    client = gspread.authorize(creds)
    
    return client

def get_price_thresholds(client, sheet_key):
    start_time = time.time()
    price_thresholds = {}

    while time.time() - start_time < 10:
        try:
            # Open the spreadsheet and get all records
            sheet = client.open_by_key(sheet_key).sheet1  # Adjust the sheet name if needed
            # Get the values from columns A and C
            gpu_names = sheet.col_values(1)[1:]  # Column A
            gpu_prices = sheet.col_values(3)[1:]  # Column C


    
            # Create a dictionary with GPU as key and price as value
            price_thresholds = {}
            for name, price in zip(gpu_names, gpu_prices):
                if name and price:  # Ensure both name and price are not empty
                    try:
                        price_thresholds[name] = float(price.replace('$', '').replace(',', ''))
                    except ValueError:
                        print(f"Skipping invalid price value for {name}: {price}")
            
            # If we have successfully retrieved and parsed the data, break out of the loop
            if price_thresholds:
                break
        except Exception as e:
            print(f"Error accessing Google Sheets: {e}")
            time.sleep(1)  # Wait for 1 second before trying again

    return price_thresholds

# Write data to Google Sheets
def write_to_google_sheets(client, spreadsheet_id, worksheet_name, data):
    # Open the spreadsheet
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    # Open the worksheet, or create it if it doesn't exist
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
    
    # Clear existing content in the worksheet
    worksheet.clear()

    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    headers = list(data[0].keys())

    # Insert headers if not already present
    if sheet.row_values(1) != headers:
        sheet.insert_row(headers, index=1)

    # Batch insert rows with rate limiting
    rows = [list(item.values()) for item in data]
    for i in range(0, len(rows), 10):  # Batch size of 10, adjust as needed
        batch = rows[i:i+10]
        sheet.append_rows(batch)
        time.sleep(10)  # Delay to avoid exceeding the quota, adjust as needed
