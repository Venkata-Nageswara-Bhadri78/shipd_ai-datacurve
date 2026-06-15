# Shipd Pebble (a.k.a DSA II) Quest Workbook

Hey everyone. While the quest is being set up on https://shipd.ai, we will be using this repository to help everyone maximize convenience when creating + solving problems.

**Any question?** Please make sure you're in the Discord and ask them in the questions channel.

## Video

[![Click here to watch 3-minute loom explanation](https://cdn.loom.com/sessions/thumbnails/9e63e099ba794e6c92b8b31a689fa95a-with-play.gif)](https://www.loom.com/share/9e63e099ba794e6c92b8b31a689fa95a).

## Setup

To get started using this to create + solve DSA questions, you should run the `init.sh` command.

Note that you might need to run the commands below first:

#### Linux/MacOS:

```bash
chmod +x init.sh
```

#### Windows:

If using Git Bash or WSL, the command above should also apply.

If using PowerShell, the scripts _should_ work without modification.

You must also have Docker and Python 3.0 installed on your machine.

<br/>
<br/>
<br/>

## Starting a new problem

To start a new problem, run the following after you run the initialization script:

```bash
./start_new_question.sh <python|javascript|cpp|java>
```

This will create a new folder in this repository, and create the following files which you will need to submit:

```
prompt.md
test file (e.g. Test.java, test.solution.mjs...)
solution file (e.g. solution.cpp, solution.py...)

```

Follow the rules in the guideline (at the bottom of this README) to create a high-quality problem.

<br/>

#### Problem bank

You are allowed to work off of existing Shipd problems if you would like. They are in [this spreadsheet](https://docs.google.com/spreadsheets/d/1u3QDAgfMVoBtC3wAc_f7Vy_re7hyES_aTc44nVeXeos/edit?gid=0#gid=0). However, these problems are only a starting point and you will need to improve their quality + difficulty to pass the Pebble quest guidelines.

<br/>
<br/>
<br/>

## Testing a problem

Testing is made simple in this repository. As long as you follow the convention that is provided in the sample files, you can run the following command from the root directory:

```bash
./test_question.sh <target_directory> <language>
```

where `target_directory` is a UUID.

When you run this, it should show the test output for the corresponding language testing framework.

## Submitting a problem

When you've finished everything, run the following:

```bash
python finish_problem.py <target_directory>
```

to convert the contents inside a folder to a `csv` format. Send this `csv` to James in the Discord server in the **#submit-questions** channel for it to get reviewed

<br/>
<br/>
<br/>

## Shipd Problem Guidelines

Here is the requirements for the Pebble qest:

**Problem must follow this format:**

- All problems are a single file
- Include all import statements used by the code in the same module

<br/>
<br/>

**Problems must be DIFFICULT:**

- There are two categories: **Medium** and **Hard**
- **Hard** questions should be unsolvable by Sonnet 3.5 or OpenAI's o1
- **Medium** questions can be solved by Sonnet 3.5 approximately 1/2 of the time

<br/>
<br/>

**Problems must be ORIGINAL:**

- these problems should be unique from existing problems on the internet. They should not be too similar to problems you can find on LeetCode, CodeForces, StackOverflow, etc…

<br/>
<br/>

**Prompts must be EXPLICIT and PRECISE:**
Include the:

- inputs + expected outputs for 2-3 tests
- unambiguous description of the task
- specific instructions on error handling
  - "if the array is empty, return a `-1`"
  - "throw an `RuntimeError` with the message 'input cannot be a negative value' if `input` is negative

**IMPORTANT:** The prompt is no longer going to be Leetcode-style format. Instead, it will be the function docstring format like the ones in `/examples/python` and `examples/java`.

<br/>
<br/>

**Testing must be COMPREHENSIVE:**

- Each language will use a corresponding testing library to write the unit tests:
  - Cpp: googletest
  - Java: junit5
  - Javascript: jest
  - Python: pytest
- There should be enough test cases (between 5-10) that covers all expected behavior of the solution
- at least 1-2 edge tests. ideally 3
- at least 2 tests that test optimalness of the solution (that should fail on unoptimal solutions and brute-force solutions)
- Runtime cutoff is 5 seconds. This means that running all the test suites should not go past this time.
