import java.util.*;

class ChuninExamSeating {
    private int m, n;
    private char[][] seats;
    private Set<Integer> chakraZones;
    private int[][] dp; // dp[row][prevMask]
    private List<Integer>[] validMasks; // precomputed valid masks for each row

    public int maxStudents(char[][] seats, List<Integer> chakraDisruptionZones) {
        if (seats == null || seats.length == 0 || seats[0].length == 0) {
            throw new IllegalArgumentException("Seats matrix cannot be null or empty.");
        }
        for (int zone : chakraDisruptionZones) {
            if (zone < 0 || zone >= seats.length) {
                throw new IllegalArgumentException("Invalid row index in Chakra Disruption Zones");
            }
        }
        this.m = seats.length;
        this.n = seats[0].length;
        this.seats = seats;
        this.chakraZones = new HashSet<>(chakraDisruptionZones);
        this.dp = new int[m + 1][1 << n];
        for (int[] row : dp) {
            Arrays.fill(row, -1);
        }

        validMasks = new List[m];
        for (int i = 0; i < m; i++) {
            validMasks[i] = new ArrayList<>();
            int available = 0;
            for (int j = 0; j < n; j++) {
                if (seats[i][j] == '.') {
                    available |= (1 << j);
                }
            }
            for (int mask = 0; mask < (1 << n); mask++) {
                // Ensure seats chosen are available.
                if ((mask & ~available) != 0) continue;
                // Check that no two adjacent seats are taken.
                if ((mask & (mask << 1)) != 0) continue;
                // Enforce chakra zone row restriction.
                if (chakraZones.contains(i) && Integer.bitCount(mask) != 1) continue;
                validMasks[i].add(mask);
            }
        }

        return backtrack(0, 0);
    }

    private int backtrack(int row, int prevMask) {
        if (row == m) {
            return 0;
        }
        if (dp[row][prevMask] != -1) {
            return dp[row][prevMask];
        }
        int maxStudents = 0;
        for (int mask : validMasks[row]) {
            if (((mask << 1) & prevMask) != 0) continue;
            if (((mask >> 1) & prevMask) != 0) continue;
            int count = Integer.bitCount(mask);
            maxStudents = Math.max(maxStudents, count + backtrack(row + 1, mask));
        }
        dp[row][prevMask] = maxStudents;
        return maxStudents;
    }
}
