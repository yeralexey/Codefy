import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

from .logger import init_logger
logger = init_logger("utils.googlejobs")


class GoogleWorker:
    def __init__(self, credentials_file, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        http_auth = credentials.authorize(httplib2.Http())
        self.sheet_service = apiclient.discovery.build('sheets', 'v4', http=http_auth)
        self.drive_service = apiclient.discovery.build('drive', 'v3', http=http_auth)

    async def sheet_create(self, user_id, user_name, rows=22, columns=1000):
        try:
            result = self.sheet_service.spreadsheets().create(body={
                'properties': {'title': f'{user_name} id{user_id}', 'locale': 'ru_RU'},
                'sheets': [{'properties': {'sheetType': 'GRID',
                                           'sheetId': 0,
                                           'title': f'{user_id}',
                                           'gridProperties': {'rowCount': rows, 'columnCount': columns}}}]
            }).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def sheet_setwide(self, sheet_id, column_index, size, end_column_index=None):
        end = column_index + 1 if end_column_index is None else end_column_index
        try:
            result = self.sheet_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body={"requests": [({"updateDimensionProperties": {
                    "range": {"sheetId": 0,
                              "dimension": "COLUMNS",
                              "startIndex": column_index,
                              "endIndex": end},
                    "properties": {"pixelSize": size},
                    "fields": "pixelSize"}})]}).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def sheet_setcolor(self, sheet_id, row_index, column_index, color, end_column_index=None, end_row_index=None):
        end_row = row_index + 1 if not end_row_index else end_row_index
        end_col = column_index + 1 if not end_column_index else end_column_index
        try:
            result = self.sheet_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body={"requests": [({"repeatCell": {
                    "range": {"sheetId": 0,
                              "startRowIndex": row_index,
                              "endRowIndex": end_row,
                              "startColumnIndex": column_index,
                              "endColumnIndex": end_col},
                    "cell": {"userEnteredFormat": {"backgroundColor": {"red": color[0],
                                                                       "green": color[1],
                                                                       "blue": color[2],
                                                                       "alpha": color[3]}}},
                    "fields": "userEnteredFormat.backgroundColor"}})]}).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def sheet_setfont(self, sheet_id, row_index, column_index, font, end_column_index=None, end_row_index=None):
        end_row = row_index + 1 if end_row_index is None else end_row_index
        end_col = column_index + 1 if end_column_index is None else end_column_index
        try:
            result = self.sheet_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body={"requests": [({"repeatCell": {
                    "range": {"sheetId": 0,
                              "startRowIndex": row_index,
                              "endRowIndex": end_row,
                              "startColumnIndex": column_index,
                              "endColumnIndex": end_col},
                    "cell": {"userEnteredFormat": {"textFormat": {"fontFamily": font[0],
                                                                  "fontSize": font[1],
                                                                  "bold": font[2]}}},
                    "fields": "userEnteredFormat.textFormat"}})]}).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def sheet_read(self, sheet_id, major_dimension, range_marks):
        try:
            result = self.sheet_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_marks,
                majorDimension=major_dimension
            ).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def sheet_write(self, sheet_id, major_dimension, range_marks, values_list):
        try:
            result = self.sheet_service.spreadsheets().values().batchUpdate(
                spreadsheetId=sheet_id, body={"valueInputOption": "USER_ENTERED",
                                              "data": [{"range": range_marks,
                                                        "majorDimension": major_dimension,
                                                        "values": values_list}]}).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def drive_set_permission(self, file_id, permission_type='anyone', user_role='reader', gmail=None,
                                   fields_to_send='id',
                                   transfer=None):
        try:
            result = self.drive_service.permissions().create(fileId=file_id,
                                                             body={'type': permission_type, 'role': user_role,
                                                                   'emailAddress': gmail},
                                                             transferOwnership=transfer,
                                                             fields=fields_to_send).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def drive_move(self, file_id, to_folder_id, from_folder_id='root'):
        try:
            result = self.drive_service.files().update(fileId=file_id, addParents=to_folder_id,
                                                       removeParents=from_folder_id).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result

    async def drive_delete(self, file_id):
        try:
            result = self.drive_service.files().delete(fileId=file_id).execute()
        except Exception as err:
            logger.exception(err)
            result = False
        return result
