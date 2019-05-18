public class Model {

    //±àÒëÆ÷²»»áºöÂÔ volatile ¹Ø¼ü×Ö
    public volatile int time;

    public synchronized int getTime(){
        return time;
    }

    public synchronized void setTime(int time){
        this.time = time;
    }


}
