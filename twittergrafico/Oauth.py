import httplib
from urllib import urlencode

data = {OAuth oauth_nonce="QP70eNmVz8jvdPevU3oJD2AfF7R7odC2XJcn4XlZJqk", oauth_callback="http%3A%2F%2Flocalhost%3A3005%2Fthe_dance%2Fprocess_callback%3Fservice_provider_id%3D11", oauth_signature_method="HMAC-SHA1", oauth_timestamp="1272323042", oauth_consumer_key="GDdmIQH6jhtmLUypg82g", oauth_signature="8wUi7m5HFQy76nowoCThusfgB%2BQ%3D", oauth_version="1.0"}
http = httplib2.Http()
headers, content = http.request("", "POST", urlencode(data))