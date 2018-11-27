import httplib, mimetypes
import urlparse

def post_multipart(scheme, host, port, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    if scheme and scheme.lower() == "http":
        h = httplib.HTTP(host, port)
    else:
        h = httplib.HTTPS(host, port)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    print (errcode, errmsg, headers)
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def get_upload_link(domain, uri):
    conn = httplib.HTTPConnection(domain)
    headers = {'Host': domain}
    headers['Authorization'] = 'Token 39299e3fd856f1d541a4ce9fbb40d2e7741b2aa4'
    conn.request("GET", uri, None, headers)
    return conn.getresponse().read()

if __name__ == '__main__':
    upload_link = get_upload_link('0.0.0.0:8000', '/api2/repos/caf3810f-45be-4bc1-af6f-329828c7f5e7/upload-link/')
    print(upload_link)
    urlparts = urlparse.urlsplit(upload_link[1:-1])
    print(urlparts) 
    fields = [('parent_dir', '/'),]
    files = [('file', 'req.txt', open('requirements.txt').read()),]

    post_multipart(urlparts.scheme, urlparts.netloc, urlparts.port,
                   urlparts.path, fields, files)
# end of http://code.activestate.com/recipes/146306/ }}}