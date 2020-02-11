import java.net.*;
import java.io.*;

class ProxyAuthenticator extends Authenticator{
    String username, password;

    public ProxyAuthenticator(String username, String password){
        this.username = username;
        this.password = password;
    }

    public PasswordAuthentication authenticate(){
        return new PasswordAuthentication(username, password.toCharArray());
    }
}


class HttpProxyDownload {

    URL url;
    String host_addr;
    String host_port;
    private String username;
    private String password;
    String html_save_path;
    String img_save_path;

    public HttpProxyDownload(final String args[]) {
        System.out.println(args[0]);
        try {
            url = new URL(args[0]);
            host_addr = args[1];
            host_port = args[2];
            username = args[3];
            password = args[4];
            html_save_path = args[5];
            img_save_path = args[6];
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Enter all the parameters");
            e.printStackTrace();
        } catch (MalformedURLException e) {
            System.out.println("Enter correct URL");
            e.printStackTrace();
        }

    }

    public static void main(final String args[]) {
        HttpProxyDownload obj = new HttpProxyDownload(args);
        HttpURLConnection url_connector;
        try{
            url_connector = (HttpURLConnection) obj.url.openConnection();
            setSystemProperties(obj.username, obj.password, obj.host_addr, obj.host_port);
            url_connector.setRequestMethod("GET");

            InputStream response = url_connector.getInputStream();
            save_html(response, obj.html_save_path);
    
        } catch (ProtocolException e) {
            e.printStackTrace();
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    public static void save_html(InputStream response, String path) throws IOException{
        BufferedReader respReader = new BufferedReader(new InputStreamReader(response));

        String respString = "";
        String temp; 
        while ((temp = respReader.readLine()) != null){
            respString += temp;
        }

        FileWriter file = new FileWriter(path);
        file.write(respString);
        file.close();

    }

    public static void setSystemProperties(String username, String password, String host, String port) {
        System.setProperty("https.proxyHost", host);
        System.setProperty("https.proxyPort", port);
        Authenticator.setDefault(new ProxyAuthenticator(username, password));
    }
}
