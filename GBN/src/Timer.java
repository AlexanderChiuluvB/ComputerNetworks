public class Timer extends Thread {

    private Model model;
    private GBNClient gbnClient;
    private SRClient srClient;
    public Timer(GBNClient gbnClient, Model model){
        this.gbnClient = gbnClient;
        this.model = model;
    }
    public Timer(SRClient srClient,Model model){
        this.srClient = srClient;
        this.model = model;
    }
    @Override
    public void run(){
        do{
            int time = model.getTime();
            if(time > 0){
                try {
                    Thread.sleep(time*1000);

                    System.out.println("\n");
                    if(gbnClient == null){
                        System.out.println("SR�ͻ��˵ȴ�ACK��ʱ");
                        srClient.timeOut();
                    }else{
                        System.out.println("GBN�ͻ��˵ȴ�ACK��ʱ");
                        gbnClient.timeOut();
                    }
                    model.setTime(0);

                } catch (InterruptedException e) {
                } catch (Exception e) {
                }
            }
        }while (true);
    }
}
