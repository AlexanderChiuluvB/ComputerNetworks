import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.util.ArrayDeque;
import java.util.Queue;
import java.util.Timer;

public class SRServer {
    private final int port = 80;
    private DatagramSocket Socket;
    private DatagramPacket packet;
    private int expectedSeq = 1;
    private Queue<Integer> cache = new ArrayDeque<>();

    public SRServer()throws Exception{

        try{
            Socket = new DatagramSocket(port);
            while(true){
                byte[]receivedData = new byte[4096];
                packet = new DatagramPacket(receivedData,receivedData.length);
                Socket.receive(packet);
                String received = new String(receivedData,0,receivedData.length);
                System.out.println(received);
                int ack = Integer.parseInt(received.substring(received.indexOf("编号:")+3).trim());

                if(ack == -1){
                    System.out.println("本次传输结束");
                    break;
                }else{
                    sendAck(ack);
                    if(ack ==expectedSeq){
                        System.out.println("服务端期待的数据编号:"+expectedSeq);
                        expectedSeq++;

                        while(cache.peek()!=null && cache.peek()==expectedSeq){
                            System.out.println("从服务端缓存中读出数据:"+cache.element());
                            cache.poll();
                            expectedSeq++;
                        }
                    }
                    else{
                        System.out.println("服务端期待的数据编号:" + expectedSeq);
                        System.out.println("+++++++++++++++++++++未收到预期数据+++++++++++++++++++++");
                        cache.add(ack);
                    }
                }
            }
        }
        catch (SocketException e){
            e.printStackTrace();
        }

    }

    public static void main(String [] args)throws Exception {
        new SRServer();
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
