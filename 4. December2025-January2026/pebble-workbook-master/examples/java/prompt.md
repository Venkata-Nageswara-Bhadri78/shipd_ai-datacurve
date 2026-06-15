```java
import java.util.*;

class ChuninExamSeating {
    /**
     * Determines maximum number of students that can be seated in an exam hall
     * while satisfying seating constraints.
     *
     * @param seats 2D matrix where '.' is usable seat and '#' is broken
     *        1 ≤ rows, cols ≤ 10
     * @param chakraDisruptionZones List of row indices that must seat exactly one student
     * @return Maximum number of students that can be seated
     * @throws IllegalArgumentException if seats matrix null/empty or invalid chakra zones
     *
     * Constraints:
     * - No adjacent students in same row
     * - No diagonally adjacent students with previous row
     * - Chakra zone rows must seat exactly one student
     *
     * Example 1:
     * Input: seats = [[".", "#", ".", "."],
     *                 [".", ".", ".", "."],
     *                 [".", "#", "#", "."],
     *                 [".", ".", ".", "#"]]
     *        chakraZones = [2]
     * Output: 7
     *
     * Example 2:
     * Input: seats = [[".", ".", "."],
     *                 [".", "#", "."],
     *                 [".", ".", "."],
     *                 ["#", "#", "#"]]
     *        chakraZones = [3]
     * Output: 6
     */
    public int maxStudents(char[][] seats, List<Integer> chakraDisruptionZones) {

    }
}
```
