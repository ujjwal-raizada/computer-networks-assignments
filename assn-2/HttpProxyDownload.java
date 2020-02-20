import java.io.*;
import java.net.*;
import java.util.Base64;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

class ClientRequest {

    Socket socket;
    String html_path;
    String img_path;
    final int proxyPort;
    final String proxyUrl;
    private String username;
    private String password;

    public ClientRequest(String proxyIP, int port, String hostURL, String user, 
                         String pass, String html_path, String img_path){    
        proxyPort = port;
        proxyUrl = proxyIP;
        username = user;
        password = pass;

        this.html_path = html_path;
        this.img_path = img_path;

        createSocket();
        connectURL(hostURL);
        sslToServer(hostURL);
    }

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

    public void connectURL(String hostURL){
        try{
            PrintWriter toProxy = new PrintWriter(socket.getOutputStream());
            BufferedReader fromProxy = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            String urlPlusPass = new String(Base64.getEncoder().encode(new String(username + ":" + password).getBytes()));

            toProxy.print("CONNECT " + hostURL + " HTTP/1.1\r\n");
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

    public void sslToServer (String hostURL){
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
            toRemote.print("\r\n");
            toRemote.flush();

            if (toRemote.checkError()) System.out.println("SSLSocketClient:  java.io.PrintWriter error");


            BufferedReader fromRemote = new BufferedReader(
                                            new InputStreamReader(
                                                sslServer.getInputStream()
                                            ));

            String response = "";
            boolean payloadAppeared = false;
            String htmlCode = "";
            while ((response = fromRemote.readLine()) != null) {
                if (payloadAppeared) htmlCode += response;
                if (response.length() == 0) payloadAppeared = true;

            }
            save_html(htmlCode);
            toRemote.close();
            fromRemote.close();
            sslServer.close();
            socket.close();
        } catch (IOException e){
            e.printStackTrace();
            System.exit(1);
        }
    }

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
        ClientRequest client = new ClientRequest(args[1], Integer.parseInt(args[2]), 
                                                    args[0], args[3], args[4], args[5], args[6]);

        
    }

}