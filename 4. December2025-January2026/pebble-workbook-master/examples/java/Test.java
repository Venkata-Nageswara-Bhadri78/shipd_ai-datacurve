import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

class ChuninExamSeatingTest {
    private final ChuninExamSeating solution = new ChuninExamSeating();

    @Test
    @DisplayName("Should correctly place 7 students with single chakra zone and broken seats")
    public void testWithBrokenSeatsAndSingleChakraZone() {
        char[][] seats = {
            { '.', '#', '.', '.' },
            { '.', '.', '.', '.' },
            { '.', '#', '#', '.' },
            { '.', '.', '.', '#' },
        };
        List<Integer> chakraZones = Arrays.asList(2);
        assertEquals(7, solution.maxStudents(seats, chakraZones));
    }

    @Test
    @DisplayName("Should correctly place 6 students with bottom row blocked")
    public void testWithBlockedBottomRow() {
        char[][] seats = {
            { '.', '.', '.' },
            { '.', '#', '.' },
            { '.', '.', '.' },
            { '#', '#', '#' }
        };
        List<Integer> chakraZones = Arrays.asList(3);
        assertEquals(6, solution.maxStudents(seats, chakraZones));
    }

    @Test
    @DisplayName("Should correctly place 34 students in large empty classroom with multiple chakra zones")
    public void testLargeEmptyClassroomWithMultipleChakraZones() {
        char[][] seats = new char[10][10];
        for (int i = 0; i < 10; i++) {
            Arrays.fill(seats[i], '.');
        }
        List<Integer> chakraZones = Arrays.asList(1, 3, 5, 7);
        assertEquals(34, solution.maxStudents(seats, chakraZones));
    }

    @Test
    @DisplayName("Should throw exception for invalid chakra zone indices")
    public void testInvalidChakraZoneIndices() {
        char[][] seats = {
            { '.', '#', '.', '.' },
            { '.', '.', '.', '.' },
            { '.', '#', '#', '.' },
            { '.', '.', '.', '#' },
        };
        assertThrows(IllegalArgumentException.class, () -> {
            solution.maxStudents(seats, Arrays.asList(-1, 5));
        }, "Invalid row index in Chakra Disruption Zones");
    }

    @Test
    @DisplayName("Should correctly place 3 students in a single column with multiple chakra zones")
    public void testSingleColumnWithMultipleChakraZones() {
        char[][] seats = {
            { '.' },
            { '.' },
            { '.' },
            { '#' },
            { '.' },
            { '.' },
            { '.' },
            { '#' },
            { '.' }
        };
        List<Integer> chakraZones = Arrays.asList(1, 2, 3, 4, 5);
        assertEquals(3, solution.maxStudents(seats, chakraZones));
    }

    @Test
    @DisplayName("Should correctly place 2 students in a single row without chakra zones")
    public void testSingleRowWithoutChakraZones() {
        char[][] seats = {{ '.', '#', '.', '.' }};
        List<Integer> chakraZones = Arrays.asList();
        assertEquals(2, solution.maxStudents(seats, chakraZones));
    }

    @Test
    @DisplayName("Should correctly place 1 student in a single row with a chakra zone")
    public void testSingleRowWithChakraZone() {
        char[][] seats = {{ '.', '#', '.', '.' }};
        List<Integer> chakraZones = Arrays.asList(0);
        assertEquals(1, solution.maxStudents(seats, chakraZones));
    }
    @Test
    @DisplayName("Should correctly place no students")
    public void testEmptyHall() {
        char[][] seats = {{}};
        List<Integer> chakraZones = Arrays.asList();
        assertThrows(IllegalArgumentException.class, () -> {
            solution.maxStudents(seats, chakraZones);
        }, "Seats matrix cannot be null or empty.");
    }

    @Test
    @DisplayName("Should correctly place 121 students in the hall.")
    public void testLargeInput() {
        char[][] seats = new char[16][16];
    for (int i = 0; i < 16; i++) {
        Arrays.fill(seats[i], '.'); 
    }

    List<Integer> chakraZones = Arrays.asList(0);
    assertEquals(121, solution.maxStudents(seats, chakraZones));
    }

    @Test
    @DisplayName("Should correctly place 4510 students in the hall.")
    public void testLargeInputWithBrokenSeats() {
        char[][] seats = new char[15][15];
    for (int i = 0; i < 15; i++) {
        if(i == 3 || i == 14  )Arrays.fill(seats[i], '#');
        else Arrays.fill(seats[i], '.'); 
    }

    List<Integer> chakraZones = Arrays.asList(10);
    assertEquals(97, solution.maxStudents(seats, chakraZones));
    }
}
