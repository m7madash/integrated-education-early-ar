const expected = [
  '2026-05-11T15:30:00Z','2026-05-11T16:00:00Z','2026-05-11T16:30:00Z',
  '2026-05-11T17:00:00Z','2026-05-11T17:30:00Z','2026-05-11T18:00:00Z',
  '2026-05-11T18:30:00Z','2026-05-11T19:00:00Z','2026-05-11T19:30:00Z'
].map(s=>new Date(s).getTime());

const ledger = [
  '2026-05-11T16:30:27Z','2026-05-11T17:30:21Z','2026-05-11T18:00:21Z',
  '2026-05-11T18:34:39Z','2026-05-11T19:30:53Z'
].map(s=>new Date(s).getTime());

const windowMs = 5*60*1000;

expected.forEach(exp => {
  let best = null;
  ledger.forEach(actual => {
    const diff = Math.abs(actual - exp);
    if (best===null || diff < best.diff) best = {time: actual, diff};
  });
  const present = best && best.diff <= windowMs/2;
  const timeStr = new Date(exp).toISOString().substring(11,16);
  const nearest = best ? new Date(best.time).toISOString().substring(11,16) + ' (+' + Math.round(best.diff/1000)+'s)' : 'none';
  console.log(timeStr, present ? '✅' : '❌', 'nearest:', nearest);
});
