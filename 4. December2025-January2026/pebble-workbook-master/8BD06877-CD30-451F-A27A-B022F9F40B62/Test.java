import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class MinimumTimeEliminationTest {
    private final Solution solution = new Solution();

    @Test
    public void testBasicCase() {
        int N = 3;
        int[] health = {1, 2, 1};
        int[] power = {2, 1, 3};
        assertEquals(1, solution.minimumTime(N, health, power));
    }

    @Test
    public void testDifferentPowers() {
        int N = 3;
        int[] health = {3, 2, 5};
        int[] power = {2, 1, 3};
        assertEquals(3, solution.minimumTime(N, health, power));
    }

    @Test
    public void testAllHighHealthLowPower() {
        int N = 4;
        int[] health = {100, 200, 300, 400};
        int[] power = {1, 1, 1, 1};
        assertEquals(400, solution.minimumTime(N, health, power));
    }

    @Test
    public void testAllHighPower() {
        int N = 5;
        int[] health = {10, 20, 30, 40, 50};
        int[] power = {100, 200, 300, 400, 500};
        assertEquals(1, solution.minimumTime(N, health, power));
    }

    @Test
    public void testIncreasingPower() {
        int N = 6;
        int[] health = {10, 15, 20, 25, 30, 35};
        int[] power = {1, 2, 3, 4, 5, 6};
        assertEquals(15, solution.minimumTime(N, health, power));
    }

    @Test
    public void testAllPlayersWithMaxValues() {
        int N = 100000;
        int[] health = new int[N];
        int[] power = new int[N];
        for (int i = 0; i < N; i++) {
            health[i] = 1000000000;
            power[i] = 1000000000;
        }
        assertEquals(1, solution.minimumTime(N, health, power));
    }

    @Test
    public void testAllPlayersHaveHealthOne() {
        int N = 5;
        int[] health = {1, 1, 1, 1, 1};
        int[] power = {5, 5, 5, 5, 5};
        assertEquals(1, solution.minimumTime(N, health, power));
    }

}
