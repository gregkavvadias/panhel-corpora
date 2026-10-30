# Genre coding: instructions for the second coder

Thank you for helping. You will label 20 short English texts (`texts/01.txt` … `texts/20.txt`) by genre. Your labels will be compared with another coder's to estimate how reliable the coding scheme is.

**Please work independently.** Don't discuss the texts with anyone, and don't look anything up about them, including the project's online repository, until you have finished.

## What to decide for each text

Assign **one fine label** to each text, from the list below, according to its **dominant communicative purpose**: what the text as a whole is mainly trying to do. Ignore how the text opens. A feature article that starts with a short anecdote and then explains or argues is labelled by what it mainly does.

| Fine label | Use it when the text mainly… | Coarse group |
|---|---|---|
| `fiction` | tells a story: a literary narrative or an extract from a novel or story | narrative |
| `personal` | recounts the writer's own experience: personal narrative or memoir | narrative |
| `biography` | tells the life of a real person, mostly in chronological order | narrative |
| `informational` | explains or reports facts, research, events or how something works | non-narrative |
| `argumentative` | argues for a position, gives an opinion or advice, or tries to persuade | non-narrative |
| `speech` | is a speech addressed to an audience | non-narrative |
| `review` | describes or summarises a book or film (a review, plot summary or study guide) rather than telling its story | non-narrative |
| `other` | fits none of the above; write the coarse group you think applies and explain | your choice |

If a text seems to fall between two labels, choose the one that best describes its *main* purpose, and say in your reason what made it hard.

## How to record your answers

Fill in `responses.csv` with one row per text:

```
NN,fine,coarse,reason
01,informational,non-narrative,"Reports a study on ..."
```

- **NN** is the text number (01–20).
- **fine** is one label from the table.
- **coarse** is `narrative` or `non-narrative`. Take it from the table, or decide it yourself for `other`.
- **reason** is one short sentence.

Please return `responses.csv` to Greg Kavvadias.
