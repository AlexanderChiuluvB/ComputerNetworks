import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.util.Timer;

public class GBNServer {
    private final int port = 80;
    private DatagramSocket Socket;
    private DatagramPacket packet;
    private int expectedSeq = 1;

    public GBNServer()throws Exception{

        try{
            Socket = new DatagramSocket(port);
            while(true){
                byte[]receivedData = new byte[4096];
                packet = new DatagramPacket(receivedData,receivedData.length);
                Socket.receive(packet);
                String received = new String(receivedData,0,receivedData.length);
                System.out.println(received);
                if(Integer.parseInt(received.substring(received.indexOf("编号:")+3).trim())==expectedSeq){
                    sendAck(expectedSeq);
                    System.out.println("服务器期待的数据编号:"+expectedSeq);
                    expectedSeq+=1;
                    System.out.println("\n");
                }else{
                    sendAck(expectedSeq-1);
                    System.out.println("服务器期待的数据编号:"+expectedSeq);
                    System.out.println("未收到预期数据\n");

                }
            }

        }
        catch (SocketException e){
            e.printStackTrace();
        }

    }

    public static void main(String [] args)throws Exception {
        new GBNServer();
    }

    public void sendAck(int ack)throws Exception{

        String sendData = "ack:"+ack;
        byte [] send = sendData.getBytes();

        int port = this.packet.getPort();
        InetAddress responseAddr = this.packet.getAddress();

        DatagramPacket sendPacket = new DatagramPacket(send,send.length,responseAddr,port);

        this.Socket.send(sendPacket);

    }


}
