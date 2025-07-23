(
  (GET_DATE_PART('YEAR', DATE1) - GET_DATE_PART('YEAR', DATE2)) * 12
  +
  (GET_DATE_PART('MONTH', DATE1) - GET_DATE_PART('MONTH', DATE2))
  +
  (
    (
      GET_DATE_PART('DAY', DATE1)
      -
      GET_DATE_PART('DAY', DATE2)
    )
    /
    IIF(
      GET_DATE_PART('MONTH', DATE1) = 2,
      IIF(
        MOD(GET_DATE_PART('YEAR', DATE1), 4) = 0
        AND (MOD(GET_DATE_PART('YEAR', DATE1), 100) != 0
             OR MOD(GET_DATE_PART('YEAR', DATE1), 400) = 0),
        29,
        28
      ),
      IIF(
        GET_DATE_PART('MONTH', DATE1) IN (1,3,5,7,8,10,12),
        31,
        30
      )
    )
  )
)
