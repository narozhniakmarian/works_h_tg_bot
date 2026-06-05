import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

class GoogleSheetsClient:
    def __init__(self, json_key_path, spreadsheet_name):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, self.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet_name = spreadsheet_name
        self.sheet = self._get_or_create_sheet()

    def _get_or_create_sheet(self):
        try:
            spreadsheet = self.client.open(self.spreadsheet_name)
            sheet = spreadsheet.sheet1
            # Check if headers exist
            headers = ["Дата", "Зміна", "Години", "Нічні", "Доплата", "Коментар"]
            if not sheet.get_all_values():
                sheet.append_row(headers)
            return sheet
        except gspread.SpreadsheetNotFound:
            raise Exception(f"Spreadsheet '{self.spreadsheet_name}' not found. Please ensure it is created and shared with the service account.")

    def add_record(self, data):
        """
        data: list [Date, Shift, Hours, NightHours, ExtraPay, Comment]
        """
        self.sheet.append_row(data)

    def get_monthly_data(self, month, year):
        records = self.sheet.get_all_records()
        filtered = []
        month_str = f"{month:02}.{year}"
        for r in records:
            date_str = str(r.get('Дата', ''))
            if month_str in date_str:
                filtered.append(r)
        return filtered

    def get_current_shift(self):
        """
        Retrieves the most recent shift from the 'Shifts' worksheet.
        """
        try:
            shift_sheet = self.client.open(self.spreadsheet_name).worksheet("Shifts")
            records = shift_sheet.get_all_values()
            if len(records) > 1:
                return int(records[-1][1])
            return 1 # Default
        except (gspread.WorksheetNotFound, ValueError):
            return 1

    def set_shift_for_week(self, start_date_str, shift):
        try:
            shift_sheet = self.client.open(self.spreadsheet_name).worksheet("Shifts")
        except gspread.WorksheetNotFound:
            shift_sheet = self.client.open(self.spreadsheet_name).add_worksheet(title="Shifts", rows="100", cols="2")
            shift_sheet.append_row(["Week Start", "Shift"])
        
        shift_sheet.append_row([start_date_str, shift])
