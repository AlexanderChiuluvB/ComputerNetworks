import com.sun.nio.sctp.SendFailedNotification;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Scanner;
import java.util.TimerTask;

import javax.swing.Timer;


public class client {

  public static int WIN_SIZE,start = 0,end,dataCount;

  public static void main(String [] args) throws Exception{

    int end_ack;

    InetAddress serverAddress = InetAddress.getByName("localhost");

    DatagramSocket clientSocket = new DatagramSocket(9999);

    byte [] sendData;

    Timer [] timers = new Timer [200];

    Scanner scanner = new Scanner(System.in);

    dataCount = scanner.nextInt();

    WIN_SIZE = scanner.nextInt();
    end =  start + WIN_SIZE-1;


    for(int i=start;i<=end;i++){

      sendData = (i+"seq").getBytes();

      DatagramPacket sendPacket = new DatagramPacket(sendData,sendData.length,serverAddress,8888);

      clientSocket.send(sendPacket);

      timers[i] = new Timer(3000,new DelayActionListener(clientSocket,i,timers));

      timers[i].start();

      System.out.println("客户端发送数据"+i);

    }//end for

    while(true){

        byte[] recvData = new byte[100];
        DatagramPacket recvPacket = new DatagramPacket(recvData,recvData.length);
        clientSocket.receive(recvPacket);
        int ack_seq = new String(recvPacket.getData()).charAt(3) - '0';

        System.out.println("客户端接收数据包"+ack_seq);
        timers[ack_seq].stop();

        if(ack_seq==dataCount-1){

          System.out.println("所有数据包接收到了");

          return;

        }
        else if(ack_seq == start){

            start++;
            end++;

            if(end>dataCount-1){
              end = dataCount -1;
            }
            sendData = (end+"Seq").getBytes();
            DatagramPacket sendPacket = new DatagramPacket(sendData,sendData.length,serverAddress,8888);
            clientSocket.send(sendPacket);
            timers[end] = new Timer(3000, new DelayActionListener(clientSocket, start, timers));
            timers[end].start();
            System.out.println("客户端发送数据包"+end);

        }
    }

  }

}


class DelayActionListener implements ActionListener{


    private DatagramSocket clientSocket;
    private int end_ack;
    private Timer [] timers;

    public DelayActionListener(DatagramSocket clientSocket,int end_ack,Timer[] timers){
        this.clientSocket = clientSocket;
        this.end_ack = end_ack;
        this.timers = timers;
    }

    @Override
    public void actionPerformed(ActionEvent e){
        int end = client.end;
        System.out.println("客户端准备重传数据"+end_ack+"--"+end);

        for(int i=end_ack;i<end;i++){

          byte [] data;
          InetAddress serverAddress = null;
          try{
                serverAddress = InetAddress.getByName("localhost");
                data = (i+"seq").getBytes();

                DatagramPacket sendPacket = new DatagramPacket(data,data.length,serverAddress,8888);

                clientSocket.send(sendPacket);

                System.out.println("客户端重传数据"+i);


          }catch (Exception E){
            E.printStackTrace();
          }
          this.timers[i].stop();
          this.timers[i].start();
        }
    }
}

