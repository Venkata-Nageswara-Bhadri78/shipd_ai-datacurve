public class Solution {
    
    public int ternarySearch(int input_array[], int left_index, int right_index) {
        if (input_array == null || input_array.length == 0 || left_index > right_index) {
            return -1;
        }

        while (left_index <= right_index) {
            if (left_index == right_index) {
                return input_array[left_index]; 
            }

            int mid_index_1 = left_index + (right_index - left_index) / 3;
            int mid_index_2 = right_index - (right_index - left_index) / 3;

            if ((mid_index_1 == 0 || input_array[mid_index_1] > input_array[mid_index_1 - 1]) &&
                (mid_index_1 == input_array.length - 1 || input_array[mid_index_1] > input_array[mid_index_1 + 1])) {
                return input_array[mid_index_1];
            }

            if ((mid_index_2 == 0 || input_array[mid_index_2] > input_array[mid_index_2 - 1]) &&
                (mid_index_2 == input_array.length - 1 || input_array[mid_index_2] > input_array[mid_index_2 + 1])) {
                return input_array[mid_index_2];
            }

            if (input_array[mid_index_1] < input_array[mid_index_1 + 1]) {
                left_index = mid_index_1 + 1;
            } else {
                right_index = mid_index_2 - 1;
            }
        }

        return -1;
    }
}
