import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class SRClient {
    private final int num = 10;
    private final int port = 80;
    private DatagramSocket socket = new DatagramSocket();
    private DatagramPacket packet;
    private InetAddress address;
    private Timer timer;
    private Model model;
    private int nextSeqNum = 1;
    private int base= 1;
    private int N = 3;//窗口大小
    private boolean[] mark;


    public static  void main(String [] args)throws Exception{
        new SRClient();
    }

    public SRClient()throws Exception{

        model = new Model();
        mark = new boolean[num+1];
        timer = new Timer(this,model);
        model.setTime(0);
        timer.start();
        while(true){

            sendData();
            byte [] bytes = new byte[4096];
            packet = new DatagramPacket(bytes,bytes.length);
            socket.receive(packet);
            String fromServer = new String(bytes,0,bytes.length);
            //累计确认
            int ack = Integer.parseInt(fromServer.substring(fromServer.indexOf("ack:")+4).trim());
            mark[ack] = true;
            System.out.println("从服务器获得的数据:"+fromServer);
            System.out.println("\n");

            if(base==ack&&base!=num){
                base++;
                for(int i=base;i<nextSeqNum;i++){
                    //发生乱序的时候，把base移动到nextseqnum
                    if(mark[i] == true){
                        base=i+1;
                    }
                }
            }else if(base==ack&&base==num){
                timer.interrupt();
                sendEnd();
                break;
            }

            if(base==nextSeqNum){
                model.setTime(3);
            }else{
                model.setTime(0);
            }
        }
    }



    public void sendData()throws Exception{
        address = InetAddress.getLocalHost();
        while(nextSeqNum<base+N && nextSeqNum<=10){
            if(nextSeqNum==3){
                nextSeqNum++;
                continue;
            }
            String clientData = "客户端发送的数据编号:"+nextSeqNum;
            System.out.println("向服务器发送的数据:"+nextSeqNum);

            byte[]data = clientData.getBytes();
            DatagramPacket packet = new DatagramPacket(data,data.length,address,port);
            socket.send(packet);
            if(nextSeqNum==base){
                model.setTime(3);
            }
            nextSeqNum++;
        }
    }

    public void sendEnd()throws Exception{
        address = InetAddress.getLocalHost();
        int end = -1;
        String clientData = "客户端发送的数据编号:"+end;
        System.out.println("向服务器发送的end signal");
        byte [] data = clientData.getBytes();
        DatagramPacket packet = new DatagramPacket(data,data.length,address,port);
        socket.send(packet);
    }

    public void timeOut()throws Exception{

        for(int i= base;i<nextSeqNum;i++){
            String clientData = "客户端重新发送的数据编号:"+i;
            System.out.println("向服务器重新发送的数据:"+i);
            byte [] data = clientData.getBytes();
            DatagramPacket packet = new DatagramPacket(data,data.length,address,port);
            socket.send(packet);
        }
    }
}
