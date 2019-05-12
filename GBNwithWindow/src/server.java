import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.ArrayList;

public class server {


  public static void main(String [] args) throws Exception{

      DatagramSocket serverSocket = new DatagramSocket(8888);

      int endReceive = -1; //最后发送的序号

      while (true){

          byte [] data = new byte[100];

          DatagramPacket receivePacket = new DatagramPacket(data,data.length);

          serverSocket.receive(receivePacket);

          int seqNum = new String(receivePacket.getData()).charAt(0) - '0';

          if(Math.random()<=0.7){
            //丢包率0.3

            if(seqNum==endReceive+1){


                byte [] ackData = new String("ack"+seqNum).getBytes();

                //get client address and port

                InetAddress clientAddress = receivePacket.getAddress();
                int clientPort = receivePacket.getPort();

                DatagramPacket sendPacket = new DatagramPacket(ackData,ackData.length,clientAddress,clientPort);

                serverSocket.send(sendPacket);

                endReceive++;

                System.out.println("服务端发送 "+ seqNum);


            }//end if
            else if(endReceive!=-1){

              byte [] ackData = new String("ack"+endReceive).getBytes();

              //get client address and port

              InetAddress clientAddress = receivePacket.getAddress();
              int clientPort = receivePacket.getPort();

              DatagramPacket sendPacket = new DatagramPacket(ackData,ackData.length,clientAddress,clientPort);

              serverSocket.send(sendPacket);

              System.out.println("服务端发送 "+ endReceive);

            }//end else


          }//end if



      }




  }

}
