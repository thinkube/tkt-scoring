# I can open the README and know which metric to ask for

You have the output of an AI system and you want a number for it. You do
not have to know the metrics beforehand: open the README and the answer is
there.

## What it does

The README has a section, "Which metric for which kind of AI output". It
has one entry for each kind of output you may have: translation, generated
or summarised text, short extracted answers, classifier labels, ranked
retrieval results, and choosing between two systems. Each entry names the
metric or metrics to ask for, the endpoint to send them to, and one line on
why.

It also tells you where the service stops: open-ended output, such as
free-form chat or reasoning answers, is not judged well by version 1. The
README points to the later milestones (model-based metrics and
LLM-as-judge) for that.

## How you use it

1. Find your kind of output in the section and read its entry.
2. Go to the worked example for that endpoint in the README. It shows a
   complete request, with the `Authorization: Bearer` header on every route
   except `/health`, and the answer the service really gives.
3. Copy the request, put in your own address, token and data, and send it.
   `references` is always one list per hypothesis, even when there is only
   one reference. To compare two systems, always send a `seed`, so that
   anyone can repeat your comparison and get the same answer.
4. Read the answer. Each result says what computed it, so two numbers from
   two projects can be compared.

A request the service cannot score is refused with a 422 and a message that
says what to send. The service never invents a number.
