import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SolutionTest { // Renamed the class

    private final Solution sol = new Solution();

    @Test
    void testBasicUnimodalArray() {
        int[] arr1 = {1, 3, 5, 7, 6, 4, 2};
        assertEquals(7, sol.ternarySearch(arr1, 0, arr1.length - 1));
    }

    @Test
    void testLargeArrayWithPeakInMiddle() {
        int[] arr2 = {10, 20, 30, 50, 100, 90, 70, 50, 30, 10};
        assertEquals(100, sol.ternarySearch(arr2, 0, arr2.length - 1));
    }

    @Test
    void testSingleElement() {
        int[] arr3 = {5};
        assertEquals(5, sol.ternarySearch(arr3, 0, arr3.length - 1));
    }

    @Test
    void testEmptyArray() {
        int[] arr4 = {};
        assertEquals(-1, sol.ternarySearch(arr4, 0, arr4.length - 1)); // Ensure ternarySearch handles empty input
    }

    @Test
    void testTwoElementsIncreasing() {
        assertEquals(5, sol.ternarySearch(new int[]{3, 5}, 0, 1));
    }

    @Test
    void testTwoElementsDecreasing() {
        assertEquals(5, sol.ternarySearch(new int[]{5, 3}, 0, 1));
    }

    @Test
    void testThreeElementsPeakInMiddle() {
        assertEquals(5, sol.ternarySearch(new int[]{1, 5, 2}, 0, 2));
    }

    @Test
    void testLargeArrayWithPeakAtStart() {
        assertEquals(20, sol.ternarySearch(new int[]{20, 18, 10, 5, 2}, 0, 4));
    }

    @Test
    void testStrictlyIncreasingArray() {
        assertEquals(5, sol.ternarySearch(new int[]{1, 2, 3, 4, 5}, 0, 4));
    }

    @Test
    void testLargeArrayWithWidePeak() {
        assertEquals(20, sol.ternarySearch(new int[]{1, 3, 7, 12, 15, 20, 20, 19, 18, 10, 5, 2}, 0, 11));
    }

    @Test
    void testInvalidRange() {
        assertEquals(-1, sol.ternarySearch(new int[]{1, 2, 3, 4, 5}, 3, 2)); // Ensure method handles invalid range
    }
}
