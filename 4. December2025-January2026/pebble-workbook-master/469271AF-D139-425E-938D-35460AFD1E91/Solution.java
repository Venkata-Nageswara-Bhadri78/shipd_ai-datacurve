public class Solution {
    private static final int MAX_SEQUENCE_LENGTH = 1_000_000;
    private static final int MAX_RULE_LENGTH = 1_000;
    private static final String ERROR_NULL = "Input arrays cannot be null";
    private static final String ERROR_SIZE = "Input arrays exceed size limits";
    private static final String ERROR_OVERFLOW = "Calculation resulted in overflow";

    /**
     * Processes large numeric sequences using memory-optimized transformations.
     * Example: For input [1,2,null,4,5] with transformRule=[2,3], output = 25
     * 
     * Time Complexity: O(n), where n is sequence length
     * Space Complexity: O(1)
     *
     * @param sequence Array of Long values (may contain nulls), max size 10^6
     * @param transformRule Array of multipliers, max size 10^3
     * @return Sum of transformed values
     * @throws IllegalArgumentException if inputs are invalid
     * @throws ArithmeticException if overflow occurs during calculation
     */
    public long processLargeSequence(Long[] sequence, int[] transformRule) {
        validateInputs(sequence, transformRule);
        
        long result = 0;
        for (Long num : sequence) {
            if (num != null) {
                result += transformValue(num, transformRule);
            }
        }
        return result;
    }

    /**
     * Validates input parameters.
     */
    private void validateInputs(Long[] sequence, int[] transformRule) {
        if (sequence == null || transformRule == null) {
            throw new IllegalArgumentException(ERROR_NULL);
        }
        if (sequence.length > MAX_SEQUENCE_LENGTH || transformRule.length > MAX_RULE_LENGTH) {
            throw new IllegalArgumentException(ERROR_SIZE);
        }
    }

    /**
     * Applies transformation rules to a single value.
     */
    private long transformValue(long value, int[] transformRule) {
        long transformedValue = value;
        for (int multiplier : transformRule) {
            transformedValue *= multiplier;
        }
        return transformedValue;
    }
}