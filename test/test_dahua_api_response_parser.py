from datetime import datetime

from src.api_dahua.api_dahua_body_parser import ApiDahuaBodyParser


class TestDahuaApiResponseParser:
    # Field constants.
    FIELD_RESULT = "result"
    FIELD_ALL_ITEM = "items"

    # Test values.
    TEST_VALUE_BODY_KEY_VALUE = """
result=2026-05-09 15:34:50\r\n"""
    TEST_VALUE_EXPECTED_RESULT = "2026-05-09 15:34:50"
    TEST_VALUE_BODY_KEY_VALUE_NESTED = """
found=100\r
items[0].Channel=1\r
items[0].StartTime=2011-1-1 12:00:00\r
items[0].EndTime=2011-1-1 13:00:00\r
items[0].Type=jpg\r
items[0].Events[0]=FaceDetection\r
items[0].FilePath=/mnt/dvr/sda0/2010/8/11/dav/15:40:50.jpg\r
items[0].CutLength=79000\r
items[0].SummaryNew[0].Key=FaceDetectionRecord\r
items[0].SummaryNew[0].Value.ImageType=GlobalSence\r
items[0].SummaryNew[0].Value.TimeStamp.UTC=134652732\r
items[0].SummaryNew[0].Value.TimeStamp.UTCMS=134\r
items[0].SummaryNew[0].Value.Sex=Man\r
items[0].SummaryNew[0].Value.Age=30\r
items[0].SummaryNew[0].Value.Glasses=1\r
items[0].SummaryNew[0].Value.Mask=2\r
items[0].SummaryNew[0].Value.Beard=1\r\n"""
    TEST_VALUE_EXPECTED_BODY_KEY_VALUE_NESTED_PARSED = {'found': 100, 'items': [{'Channel': 1, 'StartTime': datetime(2011, 1, 1, 12, 0), 'EndTime': datetime(2011, 1, 1, 13, 0), 'Type': 'jpg', 'Events': ['FaceDetection'], 'FilePath': '/mnt/dvr/sda0/2010/8/11/dav/15:40:50.jpg', 'CutLength': 79000, 'SummaryNew': [{'Key': 'FaceDetectionRecord', 'Value': {'ImageType': 'GlobalSence', 'TimeStamp': {'UTC': 134652732, 'UTCMS': 134}, 'Sex': 'Man', 'Age': 30, 'Glasses': 1, 'Mask': 2, 'Beard': 1}}]}]}
    
    
    def test_parse_key_value(self) -> None:
        body_parsed = ApiDahuaBodyParser.parse_body_key_value(self.TEST_VALUE_BODY_KEY_VALUE)
        
        value_expected = datetime.fromisoformat(self.TEST_VALUE_EXPECTED_RESULT)
        
        assert body_parsed.get(self.FIELD_RESULT) == value_expected


    def test_parse_key_value_nested(self) -> None:
        body_parsed = ApiDahuaBodyParser.parse_body_key_value(self.TEST_VALUE_BODY_KEY_VALUE_NESTED)
        
        assert body_parsed == self.TEST_VALUE_EXPECTED_BODY_KEY_VALUE_NESTED_PARSED
