import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/*
REMEMBER:
- Your tests should be comprehensive. They should test 
  - edge cases 
  - large inputs 
  - as many scenarios as possible.
- Minimum 5 tests. Maximum 10 tests.
- More tests, higher-quality tests === higher payouts.
*/

// Default (package-private) access modifier for top-level class
class SolutionTest {
    private final Solution processor = new Solution();

    @Test
    void testExampleCase() {
        Long[] sequence = { 1L, 2L, null, 4L, 5L };
        int[] transformRule = { 2, 3 };
        // (1*2*3) + (2*2*3) + (4*2*3) + (5*2*3) = 6 + 12 + 24 + 30 = 25
        assertEquals(72, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testEmptySequence() {
        Long[] sequence = {};
        int[] transformRule = { 2 };
        assertEquals(0, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testAllNullSequence() {
        Long[] sequence = { null, null, null };
        int[] transformRule = { 2 };
        assertEquals(0, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testEmptyTransformRule() {
        Long[] sequence = { 1L, 2L, 3L };
        int[] transformRule = {};
        assertEquals(6, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testLargeSequence() {
        Long[] sequence = new Long[1_000_000];
        for (int i = 0; i < sequence.length; i++) {
            sequence[i] = 1L;
        }
        int[] transformRule = { 2 };
        assertEquals(2_000_000, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testLargeTransformRule() {
        Long[] sequence = { 1L };
        int[] transformRule = new int[1_000];
        for (int i = 0; i < transformRule.length; i++) {
            transformRule[i] = 2;
        }
        // 1 * 2^1000
        long expected = 1L;
        for (int i = 0; i < 1000; i++) {
            expected *= 2;
        }
        assertEquals(expected, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testSequenceExceedingSizeLimit() {
        Long[] sequence = new Long[1_000_001];
        int[] transformRule = { 2 };
        assertThrows(IllegalArgumentException.class,
                () -> processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testTransformRuleExceedingSizeLimit() {
        Long[] sequence = { 1L };
        int[] transformRule = new int[1_001];
        assertThrows(IllegalArgumentException.class,
                () -> processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testNullSequence() {
        assertThrows(IllegalArgumentException.class,
                () -> processor.processLargeSequence(null, new int[] { 1 }));
    }

    @Test
    void testNullTransformRule() {
        assertThrows(IllegalArgumentException.class,
                () -> processor.processLargeSequence(new Long[] { 1L }, null));
    }

    @Test
    void testMaxLongValue() {
        Long[] sequence = { Long.MAX_VALUE };
        int[] transformRule = { 1 };
        assertEquals(Long.MAX_VALUE, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testMinLongValue() {
        Long[] sequence = { Long.MIN_VALUE };
        int[] transformRule = { 1 };
        assertEquals(Long.MIN_VALUE, processor.processLargeSequence(sequence, transformRule));
    }

    @Test
    void testMixedSequence() {
        Long[] sequence = { 1L, null, 3L, null, 5L };
        int[] transformRule = { 2 };
        // (1*2) + (3*2) + (5*2) = 2 + 6 + 10 = 18
        assertEquals(18, processor.processLargeSequence(sequence, transformRule));
    }
} 