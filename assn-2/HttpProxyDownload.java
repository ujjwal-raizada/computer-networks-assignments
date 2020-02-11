import java.net.*;
import java.io.*;
import java.util.ArrayList;
import java.util.regex.*;

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
            String responseText = getHTML(response);

            save_html(responseText, obj.html_save_path);
            ArrayList<String> imgURL = extractImage(responseText);
            save_image(obj.url, imgURL, obj.img_save_path);
    
        } catch (ProtocolException e) {
            e.printStackTrace();
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    public static void save_image(URL absURL, ArrayList<String> imgURL, String path) throws IOException{
        if (imgURL.size() == 0) {
            System.out.println("Now images found !");
        }
        else{
            for (String img: imgURL){
                String[] imgTags = img.split(" ");
                String srcVal = null;
                for (String attr: imgTags){
                    if (attr.length() < 3) continue;
                    else if (attr.substring(0, 3).equals("src") == true){
                        srcVal = attr.substring(5, attr.length() - 1);
                        break;
                    }
                }
                if (srcVal == null){
                    System.out.println("Src Tag not found !");
                }
                else {
                    URL srcUrl = new URL(absURL, srcVal);
                    InputStream in = srcUrl.openStream();
                    OutputStream out = new FileOutputStream(path);

                    byte[] b = new byte[2048];
                    int length;
                
                    while ((length = in.read(b)) != -1) {
                        out.write(b, 0, length);
                    }
                
                    in.close();
                    out.close();
                }
            }
        }
    }

    public static String getHTML(InputStream response) throws IOException{
        BufferedReader respReader = new BufferedReader(new InputStreamReader(response));
        String respString = "";
        String temp; 
        while ((temp = respReader.readLine()) != null){
            respString += temp;
        }
        return respString;
    }

    public static ArrayList<String> extractImage(String htmlCode) throws IOException{
        Pattern img_tag = Pattern.compile("<img (.*?)>");
        Matcher matcher = img_tag.matcher(htmlCode);

        ArrayList<String> listImages = new ArrayList<String>();
        while (matcher.find()){
            listImages.add(matcher.group(0));
        }
        return listImages;
    }

    public static void save_html(String writeString, String path) throws IOException{
        FileWriter file = new FileWriter(path);
        file.write(writeString);
        file.close();

    }

    public static void setSystemProperties(String username, String password, String host, String port) {
        System.setProperty("https.proxyHost", host);
        System.setProperty("https.proxyPort", port);
        Authenticator.setDefault(new ProxyAuthenticator(username, password));
    }
}
