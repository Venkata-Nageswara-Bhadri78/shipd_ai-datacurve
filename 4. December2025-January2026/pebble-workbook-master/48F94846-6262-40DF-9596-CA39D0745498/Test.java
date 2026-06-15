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
class computeLevenshteinDistanceTest {
    private final Solution wordProcessor = new Solution();

    @Test
    void testEmptyStrings() {
        assertEquals(0, wordProcessor.computeLevenshteinDistance("", ""));
    }

    @Test
    void testNullInputString1() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            wordProcessor.computeLevenshteinDistance(null, "sitting");
        });
        assertNotNull(exception);
    }

    @Test
    void testNullInputString2() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            wordProcessor.computeLevenshteinDistance("kitten", null);
        });
        assertNotNull(exception);
    }

    @Test
    void testBothInputsNull() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            wordProcessor.computeLevenshteinDistance(null, null);
        });
        assertNotNull(exception); 
    }

    @Test
    void testEmptyStringAndNonEmptyString() {
        assertEquals(3, wordProcessor.computeLevenshteinDistance("", "abc"));
        assertEquals(3, wordProcessor.computeLevenshteinDistance("abc", ""));
    }

    @Test
    void testIdenticalStrings() {
        assertEquals(0, wordProcessor.computeLevenshteinDistance("hello", "hello"));
    }

    @Test
    void testSimpleStrings() {
        assertEquals(3, wordProcessor.computeLevenshteinDistance("kitten", "sitting"));
        assertEquals(5, wordProcessor.computeLevenshteinDistance("intention", "execution"));
    }

    @Test
    void testStringsWithDifferentLengths() {
        assertEquals(6, wordProcessor.computeLevenshteinDistance("abcdefgh", "ab"));
        assertEquals(6, wordProcessor.computeLevenshteinDistance("ab", "abcdefgh"));

    }

    @Test
    void testStringsWithUppercaseAndLowercase() {
        assertEquals(1, wordProcessor.computeLevenshteinDistance("Hello", "hello")); 
        assertEquals(4, wordProcessor.computeLevenshteinDistance("apple", "ApplePie"));
    }

    @Test
    void testStringsWithDigitsAndSpecialChars() {
        assertEquals(6, wordProcessor.computeLevenshteinDistance("123abc", "abc456"));
        assertEquals(4, wordProcessor.computeLevenshteinDistance("!@#$", "1234"));
        assertEquals(5, wordProcessor.computeLevenshteinDistance("!@#$%", "12345"));
    }

    @Test
    void testLongStrings() {
        String str1 = "pneumonoultramicroscopicsilicovolcanoconiosis";
        String str2 = "pneumonoultramicroscopicsilicovolcanoconiosiss";
        assertEquals(1, wordProcessor.computeLevenshteinDistance(str1, str2));
    }

    @Test
    void testVeryLongStrings() { 
        String str1 = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz";
        String str2 = "abcdefghijkmnopqrstuvwxyzabcdefghijkmnopqrstuvwxyzabcdefghijkmnopqrstuvwxyz";
        int startTime = (int) System.currentTimeMillis();
        int distance = wordProcessor.computeLevenshteinDistance(str1, str2);
        int endTime = (int) System.currentTimeMillis();
        System.out.println("Time taken for very long strings: " + (endTime - startTime) + "ms");
        assertEquals(3, distance); 
        assertTrue((endTime - startTime) < 500, "Test took too long. Optimize your solution for efficiency."); 
    }

    @Test
    void testStringsWithSpaces() {
        assertEquals(1, wordProcessor.computeLevenshteinDistance("hello world", "hello  world"));
        assertEquals(1, wordProcessor.computeLevenshteinDistance(" hello world", "hello world"));
    }

    @Test
    void testStringsWithUnicode() {
        assertEquals(1, wordProcessor.computeLevenshteinDistance("café", "cafe")); 
        assertEquals(0, wordProcessor.computeLevenshteinDistance("你好", "你好")); 
    }
} 
