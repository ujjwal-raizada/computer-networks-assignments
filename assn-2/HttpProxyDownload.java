/* BeginGroupMembers */
/* f20170124@hyderabad.bits-pilani.ac.in Pranjal Gupta */
/* f20171398@hyderabad.bits-pilani.ac.in Ujjwal Raizada */
/* f20170218@hyderabad.bits-pilani.ac.in Daksh Yashlaha */
/* f20171454@hyderabad.bits-pilani.ac.in Simran Sandhu */
/* EndGroupMembers */

import java.io.*;
import java.net.*;
import java.util.Base64;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

class DownloadRequest {

    Socket socket;
    String html_path;
    String img_path;
    final int proxyPort;
    final String proxyUrl;
    private String username;
    private String password;

    /**
     * Constructor for Initialising Class Object
     * @param proxyIP
     * @param port
     * @param hostURL
     * @param user
     * @param pass
     * @param html_path
     * @param img_path
     */
    public DownloadRequest(String proxyIP, int port, String hostURL, String user,
                         String pass, String html_path, String img_path){
        proxyPort = port;
        proxyUrl = proxyIP;
        username = user;
        password = pass;

        this.html_path = html_path;
        this.img_path = img_path;

        createSocket();
        connectURL(hostURL);
        String htmlCode = extractHTML(hostURL);
        extractAndSaveImage(hostURL, htmlCode);
    }

    /**
     * Creates socket connection between the user and the proxy server
    */
    void createSocket() {
        try {
            socket = new Socket(proxyUrl, proxyPort);
        } catch (UnknownHostException e){
            e.printStackTrace();
            System.exit(1);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    /**
     * Issues a CONNECT request to the proxy server
     * @param hostURL
    */
    public void connectURL(String hostURL){
        try{
            PrintWriter toProxy = new PrintWriter(socket.getOutputStream());
            BufferedReader fromProxy = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            String urlPlusPass = new String(Base64.getEncoder().encode(new String(username + ":" + password).getBytes()));

            toProxy.print("CONNECT " + hostURL + " HTTP/1.0\r\n");
            toProxy.print("Proxy-Authorization: Basic " + urlPlusPass + "\r\n");
            toProxy.print("\r\n");
            toProxy.flush();

            String response = fromProxy.readLine();
            System.out.println("Proxy Connection : " + response);

            if (!response.contains("200")) {
                System.out.println("Couldn't Establish Connection");
            }
        } catch (IOException e){
            e.printStackTrace();
            System.exit(1);
        }
    }


    /**
     * Makes a GET request through the Proxy-Socket by wrapping it over a SSL
     * Socket and extracts the HTML (Payload) from the packet(s) received from the
     * response.
     * @param hostURL
     * @return htmlCode (String representation of HTML)
     */
    public String extractHTML (String hostURL){
        String htmlCode = "";
        try{
            SSLSocketFactory factorySocket = (SSLSocketFactory) SSLSocketFactory.getDefault();
            SSLSocket sslServer = (SSLSocket) factorySocket.createSocket(socket, hostURL, proxyPort, true);
            System.out.println("Server Connection: SSL Connection established");

            sslServer.startHandshake();
            PrintWriter toRemote = new PrintWriter(
                                    new BufferedWriter(
                                    new OutputStreamWriter(
                                        sslServer.getOutputStream()
                                    )));

            toRemote.print("GET / HTTP/1.0\r\n");
            toRemote.print("Host: " + hostURL + "\r\n");
            toRemote.print("\r\n");
            toRemote.flush();

            if (toRemote.checkError()) System.out.println("SSLSocketClient:  java.io.PrintWriter error");


            BufferedReader fromRemote = new BufferedReader(
                                            new InputStreamReader(
                                                sslServer.getInputStream()
                                            ));

            String response = "";
            boolean payloadAppeared = false;
            while ((response = fromRemote.readLine()) != null) {
                if (payloadAppeared) htmlCode += response;
                if (response.length() == 0) payloadAppeared = true;
            }
            save_html(htmlCode);
        } catch (IOException e){
            e.printStackTrace();
            System.exit(1);
        }
        return htmlCode;
    }

    /**
     * Extracts image (<img> tag) from the HTML code and downloads the first image
     * from the HTML code.
     * To download all the image(s), comment the if-condition following the save_image()
     * call in the method.
     * @param hostURL
     * @param htmlCode
     */
    public void extractAndSaveImage(String hostURL, String htmlCode){
        Pattern img_tag = Pattern.compile("<img[^>]*src=[\"']([^\"^']*)", Pattern.CASE_INSENSITIVE);
        Matcher matcher = img_tag.matcher(htmlCode);

        while (matcher.find()){
            boolean status = save_image(hostURL, matcher.group(1));
            if (status) return;
        }
    }

    /**
     * Given the imgURL extracted, this method downloads the image using socket.
     * @param hostURL
     * @param imgURL
     * @return False if any error occurs, else True
     */
    public boolean save_image(String hostURL, String imgURL){
        if (imgURL.substring(0,5).equals("https") == false) imgURL = "/" + imgURL;
        try{
            createSocket();
            connectURL(hostURL);
            SSLSocketFactory factorySocket = (SSLSocketFactory) SSLSocketFactory.getDefault();
            SSLSocket sslServer = (SSLSocket) factorySocket.createSocket(socket, hostURL, proxyPort, true);
            System.out.println("Server Connection: SSL Connection established");

            sslServer.startHandshake();
            PrintWriter toRemote = new PrintWriter(
                                    new BufferedWriter(
                                    new OutputStreamWriter(
                                        sslServer.getOutputStream()
                                    )));

            toRemote.print("GET "+ imgURL +" HTTP/1.0\r\n");
            toRemote.print("Host: " + hostURL + "\r\n");
            toRemote.print("\r\n");
            toRemote.flush();

            OutputStream dos = new BufferedOutputStream(new FileOutputStream(img_path));
            InputStream in = sslServer.getInputStream();
            int count, offset;
            byte[] buffer = new byte[2048];
            boolean eohFound = false;


            while ((count = in.read(buffer)) != -1){
                offset = 0;
                if(!eohFound){
                    String string = new String(buffer, 0, count);
                    int indexOfEOH = string.indexOf("\r\n\r\n");
                    if(indexOfEOH != -1) {
                        count = count-indexOfEOH-4;
                        offset = indexOfEOH+4;
                        eohFound = true;
                    } else {
                        count = 0;
                    }
                }
                dos.write(buffer, offset, count);
                dos.flush();
            }
            in.close();
            dos.close();
            return true;
        } catch (IOException e){
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Saves the HTML (payload) received from the response packets
     * in an html file specified by this.html_path variable.
     * @param writeString
     * @throws IOException
     */
    public void save_html(String writeString) throws IOException{
        FileWriter file = new FileWriter(this.html_path);
        file.write(writeString);
        file.close();
    }

}


class HttpProxyDownload{

    public static void main(String args[]){
        if (args.length != 7) {
            System.out.format("Expected 7, found %s args\n", args.length);
            return;
        }
        new DownloadRequest(args[1], Integer.parseInt(args[2]),
                                                    args[0], args[3], args[4], args[5], args[6]);


    }

}
