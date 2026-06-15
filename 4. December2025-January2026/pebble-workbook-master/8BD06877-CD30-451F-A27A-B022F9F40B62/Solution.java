// Default (package-private) access modifier for top-level class
import java.util.*;

class Solution {

    public static int minimumTime(int N, int health[], int[] power) {
        Deque<int[]> dq = new ArrayDeque<>();
        int answer = 1 + (health[1]-1)/power[0];
        int[] a = {power[0], answer};
        dq.push(a);
        for(int i=1 ; i<N ; i++) {
            int currTime = 0;
            while(true) {
                if(dq.isEmpty()) {
                    currTime += 1 + (health[i]-1)/power[0];
                    dq.push(new int[] {power[i], currTime});
                    answer = Math.max(answer, currTime);
                    break;
                }
                int[] array = dq.pop();
                int time = 1 + (health[i]-1)/array[0];
                if(time <= array[1]) {
                    if(array[1]-time>0) {
                        dq.push(new int[] {array[0], (array[1]-time)});
                    }
                    dq.push(new int[] {power[i], currTime+time});
                    answer = Math.max(answer, currTime+time);
                    break;
                }
                else {
                    currTime += array[1];
                    health[i] -= array[0]*array[1];
                }
            }
        }
        return answer;
    }
}