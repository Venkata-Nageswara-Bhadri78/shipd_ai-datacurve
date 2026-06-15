class Solution {
    /**
     * Computes the Levenshtein distance (edit distance) between two strings.
     * The Levenshtein distance algorithm computes the minimum number of
     * single-character edits (insertions, deletions, or replacements) required to
     * transform one string into the other. 
     *
     * @param str1 The first input string.
     * @param str2 The second input string.
     * @return The Levenshtein distance between str1 and str2.
     * @throws IllegalArgumentException If either input string is null.
     */
    public int computeLevenshteinDistance(String str1, String str2) {
        // Check if any of the input strings are null
        if (str1 == null || str2 == null) {
            throw new IllegalArgumentException("Input strings must not be null");
        }

        int m = str1.length();
        int n = str2.length();

        if (m == 0) { // If str1 is empty, the edit distance is the length of str2
            return n;
        }

        if (n == 0) { // If str2 is empty, the edit distance is the length of str1
            return m;
        }

        // Optimize memory: Ensure str1 is the longer string (or equal)
        if (m < n) {
            String temp = str1;
            str1 = str2;
            str2 = temp;
            m = str1.length();
            n = str2.length();
        }


        // Create a 1D DP array of length of the shorter string + 1
        int[] dp = new int[n + 1];

        // Initialize the DP array
        // dp[j] represents the edit distance between an empty
        // string and the first j characters of str2
        for (int j = 0; j <= n; j++) {
            dp[j] = j; 
        }

        // Compute the Levenshtein distance using dynamic programming.
        for (int i = 1; i <= m; i++) {
            int previous = dp[0];
            dp[0] = i;

            for (int j = 1; j <= n; j++) {
                int oldVal = dp[j];

                if (str1.charAt(i - 1) == str2.charAt(j - 1)) {
                    // If the current characters match, the cost is the same as
                    // the cost to transform the previous substrings (the diagonal value)
                    dp[j] = previous;
                } else {
                    // If the characters don't match, the cost is 1 (for the edit) plus the
                    // minimum of the costs of the three possible operations:
                    // 1. Insertion (from the left: dp[j-1])
                    // 2. Deletion (from above: previous)
                    // 3. Substitution (from the diagonal: previous)
                    dp[j] = 1 + Math.min(previous, Math.min(dp[j - 1], dp[j]));
                }

                // Update 'previous' with the old value for the next column
                previous = oldVal;
            }
        }

        // The result is stored in the last element of the dp array.
        return dp[n];
    }
}