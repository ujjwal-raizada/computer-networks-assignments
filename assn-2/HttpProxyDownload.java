import java.io.*;
import java.net.*;
import java.util.Base64;

class ClientRequest {

    String html_path;
    String img_path;
    Socket socket;

    public ClientRequest(String proxyUrl, int proxyPort, String url, String username, 
                         String password, String html_path, String img_path) {
        createSocket(proxyUrl, proxyPort);
        connectURL(url, username, password);
        this.html_path = html_path;
        this.img_path = img_path;
    }

    public void createSocket(String proxyUrl, int proxyPort) {
        try {
            socket = new Socket(proxyUrl, proxyPort);
            System.out.println("Connection Established");
        } catch (UnknownHostException e){
            e.printStackTrace(); 
            System.exit(1);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    public void connectURL(String url, String user, String pass){
        try{
            PrintWriter toProxy = new PrintWriter(socket.getOutputStream());
            String urlPlusPass = new String(Base64.getEncoder().encode(new String(user + ":" + pass).getBytes()));

            toProxy.print("CONNECT " + url + " HTTP/1.1\r\n");
            toProxy.print("Proxy-Authorization: Basic " + urlPlusPass + "\r\n");
            toProxy.print("\r\n");
            toProxy.flush();
            
            BufferedReader buf = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String response = buf.readLine();
            System.out.println("Response : " + response);
            if (!response.contains("200")) {;
                System.out.println("Couldn't Establish Connection");
                System.exit(0);
            }
        } catch (IOException e){
            e.printStackTrace();
        } 
    }
}


class HttpProxyDownload{
    
    public static void main(String args[]){
        if (args.length != 7) {
            System.out.format("Expected 7, found %s args\n", args.length);
            return;
        }
        ClientRequest client = new ClientRequest(args[1], Integer.parseInt(args[2]), args[0], 
                                                 args[3], args[4], args[5], args[6]);
    
        
    }

}