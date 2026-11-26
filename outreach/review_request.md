# Review request emails (draft, not sent)

Goal: get independent people to check that V1's comparison against the FORCE 2020 competition is fair and the
numbers are real, and ask for more data. We ask them to check the method, not to endorse a product.
No mention of AI or software, as with the data requests. The report link and the code must be viewable by them first.

## Recent graduates and students (geoscience, geophysics, petroleum engineering, data science)
Subject: Would you sanity-check a well-log lithology result?

Hi {first_name},

I'm a young entrepreneur teaching myself petrophysics and geophysics. As practice, I took the public FORCE 2020
lithology dataset (118 North Sea wells) and predicted rock type in the 10 hidden test wells under the original
competition rules, then scored it with the organizers' own penalty matrix and scoring code.

The short version: my first attempt scores -0.62 (76% of depths right). The winning team scored -0.47 (80.5%).
Everything is laid out here, including a script that re-scores every finalist and my results from the
organizers' own files: {report_link}

Would you be willing to spend 15 minutes checking whether the comparison is fair and the numbers hold up? Honest
criticism is exactly what I'm after. If it looks sound, a short note saying so (and what you checked) would mean a
lot. And if you know of other public well-log or fiber-optic (DAS) datasets with known answers, I'd love pointers.

Thank you,
Tobias Lee

## Professors and researchers
Subject: Independent check of a FORCE 2020 lithology benchmark

Dear Professor {last_name},

I'm a young entrepreneur learning subsurface data interpretation, and I've been working through public benchmarks
to measure my progress honestly. On the FORCE 2020 lithology dataset I followed the competition's train / open-test
/ hidden-test split and scored the hidden wells once with the organizers' penalty matrix: -0.62 (76% accuracy),
against -0.47 (80.5%) for the winning team. I've also verified the published finalist scores from their stored
predictions.

The full write-up, code and a one-command verification script are here: {report_link}

If you or a student in your group could look over the method for fairness and mistakes, I'd be very grateful, and
I'd welcome any suggestions for labelled well-log or DAS datasets I should test against next.

Kind regards,
Tobias Lee
