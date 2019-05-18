import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class GBNClient {


    private final int port = 80;
    private DatagramSocket socket = new DatagramSocket();
    private DatagramPacket packet;
    private InetAddress address;
    private Timer timer;
    private Model model;
    private int nextSeqNum = 1;
    private int base= 1;
    private int N = 5;//���ڴ�С

    public static  void main(String [] args)throws Exception{
        new GBNClient();
    }

    public GBNClient()throws Exception{

        model = new Model();
        timer = new Timer(this,model);
        model.setTime(0);
        timer.start();
        while(true){

            sendData();
            byte [] bytes = new byte[4096];
            packet = new DatagramPacket(bytes,bytes.length);
            socket.receive(packet);
            String fromServer = new String(bytes,0,bytes.length);

            //�ۼ�ȷ��
            int ack = Integer.parseInt(fromServer.substring(fromServer.indexOf("ack:")+4).trim());
            base = ack+1;

            if(base==nextSeqNum){
                model.setTime(0);
            }else{
                model.setTime(3);
            }
            System.out.println("�ӷ�������õ�����:"+fromServer);
            System.out.println("\n");
        }
    }



    public void sendData()throws Exception{
        address = InetAddress.getLocalHost();
        while(nextSeqNum<base+N && nextSeqNum<=10){
            if(nextSeqNum==4){
                nextSeqNum++;
                continue;
            }
            String clientData = "�ͻ��˷��͵����ݱ��:"+nextSeqNum;
            System.out.println("����������͵�����:"+nextSeqNum);

            byte[]data = clientData.getBytes();
            DatagramPacket packet = new DatagramPacket(data,data.length,address,port);
            socket.send(packet);
            if(nextSeqNum==base){
                model.setTime(3);
            }
            nextSeqNum++;
        }
    }

    public void timeOut()throws Exception{

        for(int i=base;i<nextSeqNum;i++){
            String clientData = "�ͻ������·��͵����ݱ��:"+i;
            System.out.println("����������·��͵�����:"+i);
            byte [] data = clientData.getBytes();
            DatagramPacket packet = new DatagramPacket(data,data.length,address,port);
            socket.send(packet);
        }
    }
}
