/**
 * Curriculum-to-careers data, loaded from the CSVs next to this file.
 *
 * EDIT THE CSVs, NOT THIS FILE, NOT THE PAGE.
 *   curriculum-careers.csv     Table A — one row per course, per program
 *   careers-salary.csv         Table B — one row per job role, per program
 *   careers-focus-areas.csv    Table F — the B.S. focus areas
 *   careers-role-crosswalk.csv the name-level pairing between A and B
 *
 * TWO PROGRAMS, TWO REPORTS (2026-10-04). Table A and Table B each carry a
 * `program` column, and Table B also carries `source`, because the two
 * programs were measured by two different Lightcast reports:
 *
 *   M.S. in Business Analytics  Q1 2026 data set, CIP 30.7102,
 *                               Master's-degree filter, postings Jan–Mar 2026
 *   B.S. in Analytics           Q2 2026 data set, CIPs 30.7101/7102/7103/
 *                               7104/7199, Bachelor's-degree filter,
 *                               postings Mar 2025 – Mar 2026
 *
 * Five occupations therefore appear twice with the same national median and
 * different growth and job counts. That is the data, not a duplicate: both
 * rows stay, the page explains why, and everything keyed to a Table B row
 * (anchors, Table A's role links, the role-button course counts) is scoped by
 * program so a master's course never links to a bachelor's figure.
 *
 * Read with the `?raw` glob the guides manifest already uses — the files are
 * read at build time, so nothing ships to the browser but the rendered rows.
 */
const files = import.meta.glob<string>('/src/data/*.csv', {
  query: '?raw',
  import: 'default',
  eager: true,
});

/**
 * RFC 4180-ish CSV reader: quoted fields, embedded commas, newlines and `""`
 * escapes. Deliberately hand-written — the three files here are a few hundred
 * bytes and do not justify a dependency.
 */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = '';
  let quoted = false;
  let i = 0;
  // Strip a UTF-8 BOM (Excel writes one) and normalise CRLF.
  const src = text.replace(/^﻿/, '').replace(/\r\n?/g, '\n');

  const endField = () => {
    row.push(field);
    field = '';
  };
  const endRow = () => {
    endField();
    // Skip blank trailing lines.
    if (row.length > 1 || row[0] !== '') rows.push(row);
    row = [];
  };

  while (i < src.length) {
    const c = src[i];
    if (quoted) {
      if (c === '"') {
        if (src[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        }
        quoted = false;
        i += 1;
        continue;
      }
      field += c;
      i += 1;
      continue;
    }
    if (c === '"' && field === '') {
      quoted = true;
      i += 1;
      continue;
    }
    if (c === ',') {
      endField();
      i += 1;
      continue;
    }
    if (c === '\n') {
      endRow();
      i += 1;
      continue;
    }
    field += c;
    i += 1;
  }
  if (field !== '' || row.length) endRow();
  return rows;
}

/** Header row -> array of records, keyed by column name. */
function records(csvPath: string): Record<string, string>[] {
  const raw = files[csvPath];
  if (raw === undefined) throw new Error(`Missing data file: ${csvPath}`);
  const [header, ...body] = parseCsv(raw);
  if (!header) throw new Error(`Empty data file: ${csvPath}`);
  return body.map((cells) => {
    const rec: Record<string, string> = {};
    header.forEach((name, i) => {
      rec[name.trim()] = (cells[i] ?? '').trim();
    });
    return rec;
  });
}

export interface CrosswalkRow {
  program: string;
  level: string;
  course: string;
  /** Verbatim "Skills & tools you'll gain" cell. */
  skills: string;
  /** Verbatim "Job roles it supports" cell. */
  roles: string;
  /** `roles` split on commas — the unit the role filter and the links work on. */
  roleTokens: string[];
}

export interface SalaryRow {
  role: string;
  /** Which program's report this row belongs to. */
  program: string;
  /** Verbatim report name, e.g. "Lightcast Q2 2026". */
  source: string;
  /** Verbatim, e.g. "$112,174". */
  medianSalary: string;
  /** Verbatim, e.g. "+28.10%" or "−1.74%" (U+2212). */
  projectedGrowth: string;
  /** Verbatim 2026 national job count, e.g. "91,945". */
  jobs2026: string;
  /** Digits of `medianSalary`, for the default sort only. */
  salaryValue: number;
  /** `projectedGrowth` as a signed number — negative stays negative. */
  growthValue: number;
  /** Source-file position, the tie-break for every sort. */
  index: number;
  /** Fragment id this row is linked to from Table A. */
  anchor: string;
}

/** `Data Scientists` -> `data-scientists`. */
function slug(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * `Data Scientists` + `B.S. in Analytics` -> `salary-b-s-in-analytics-data-scientists`.
 *
 * The program is in the id because the same occupation now has one row per
 * program; without it the page would emit duplicate fragment ids and Table A's
 * links would all land on whichever row happened to be first.
 */
export function anchorFor(role: string, program: string): string {
  return 'salary-' + slug(program) + '-' + slug(role);
}

/**
 * Signed percentage out of a verbatim cell.
 *
 * Lightcast writes the one declining occupation as a minus, and the CSV keeps
 * a real U+2212 MINUS SIGN so the page renders it correctly. Stripping
 * non-digits — which is all the salary column needs — would turn −1.74% into
 * +1.74 and sort Computer Programmers into the middle of the table.
 */
function percentValue(s: string): number {
  const m = s.replace(/[−–—]/g, '-').match(/-?\d+(?:\.\d+)?/);
  return m ? Number(m[0]) : 0;
}

export const crosswalk: CrosswalkRow[] = records('/src/data/curriculum-careers.csv').map((r) => ({
  program: r.program,
  level: r.level,
  course: r.course,
  skills: r.skills,
  roles: r.roles,
  roleTokens: r.roles
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean),
}));

/**
 * Table B, salary descending — the page's default order, and the "unsorted"
 * state its column sorts return to.
 *
 * Equal salaries tie-break on file position, which puts the master's row
 * above the bachelor's one. The five occupations that appear in both reports
 * have identical national medians, so this is what lands each pair together
 * instead of scattering them.
 */
export const salaries: SalaryRow[] = records('/src/data/careers-salary.csv')
  .map((r, i) => ({
    role: r.role,
    program: r.program,
    source: r.source,
    medianSalary: r.median_salary,
    projectedGrowth: r.projected_growth,
    jobs2026: r.jobs_2026,
    salaryValue: Number(r.median_salary.replace(/[^0-9.]/g, '')) || 0,
    growthValue: percentValue(r.projected_growth),
    index: i,
    anchor: anchorFor(r.role, r.program),
  }))
  .sort((a, b) => b.salaryValue - a.salaryValue || a.index - b.index);

/** Distinct programs in Table B, alphabetical — the Table B filter's options. */
export const salaryPrograms: string[] = [...new Set(salaries.map((s) => s.program))].sort((a, b) =>
  a.localeCompare(b),
);

/**
 * Which Table A role token belongs to which Table B row.
 *
 * The two tables name the same jobs differently (Table A says "Data Scientist",
 * Lightcast says "Data Scientists"), so the pairing is spelled out in
 * careers-role-crosswalk.csv rather than guessed by string matching. A role on
 * either side with no pair simply does not link — that is a true statement
 * about the data, not a bug.
 */
const pairs = records('/src/data/careers-role-crosswalk.csv');

/** Table A role token (lower-cased) -> the Table B *role name* it pairs with. */
const tokenToSalaryRole = new Map<string, string>();
/** Table B role -> the Table A role tokens that stand for it. */
export const salaryToTokens = new Map<string, string[]>();

for (const p of pairs) {
  if (!salaries.some((s) => s.role === p.salary_role)) continue;
  tokenToSalaryRole.set(p.crosswalk_role.toLowerCase(), p.salary_role);
  salaryToTokens.set(p.salary_role, [
    ...(salaryToTokens.get(p.salary_role) ?? []),
    p.crosswalk_role,
  ]);
}

/**
 * The Table B row a Table A role token points at, *within its own program*.
 *
 * A master's course names "Data Scientist"; so does a bachelor's course. They
 * must not link to the same salary row, because the two programs were measured
 * by different reports. `undefined` means the token has no priced occupation
 * in that program — the page renders it as plain text, which is a true
 * statement about the data.
 */
export function salaryForToken(program: string, token: string): SalaryRow | undefined {
  const role = tokenToSalaryRole.get(token.toLowerCase());
  if (!role) return undefined;
  return salaries.find((s) => s.role === role && s.program === program);
}

/** Distinct Table A role tokens, alphabetical. */
export const roleTokens: string[] = [...new Set(crosswalk.flatMap((r) => r.roleTokens))].sort(
  (a, b) => a.localeCompare(b),
);

export interface RoleOption {
  /** `|`-joined token list; what the <select> and the Table B buttons carry. */
  value: string;
  label: string;
}

/**
 * The role filter's options: one per Table A role token, plus a combined option
 * for any Table B role that pairs with more than one token — so that a Table B
 * click always has an option to select. Today every pairing is 1:1 and no
 * combined option is produced.
 */
export const roleOptions: RoleOption[] = [
  ...roleTokens.map((t) => ({ value: t, label: t })),
  ...[...salaryToTokens.values()]
    .filter((tokens) => tokens.length > 1)
    .map((tokens) => ({ value: tokens.join('|'), label: tokens.join(' / ') })),
];

/** The filter value a Table B row's button applies to Table A. */
export function roleFilterValueFor(role: string): string {
  return (salaryToTokens.get(role) ?? []).join('|');
}

/**
 * Distinct programs in Table A. The page renders a program filter only when
 * this has more than one entry; with a single program the control would be a
 * dropdown with one option.
 */
export const programs: string[] = [...new Set(crosswalk.map((r) => r.program))].sort((a, b) =>
  a.localeCompare(b),
);

/**
 * How many Table A courses a Table B row has, via the crosswalk pairs —
 * counted inside that row's own program, so the master's "Statisticians" row
 * (no master's course names a Statistician) stays plain text while the
 * bachelor's one becomes a filter button.
 */
export function courseCountFor(role: string, program: string): number {
  const tokens = (salaryToTokens.get(role) ?? []).map((t) => t.toLowerCase());
  if (!tokens.length) return 0;
  return crosswalk.filter(
    (r) => r.program === program && r.roleTokens.some((t) => tokens.includes(t.toLowerCase())),
  ).length;
}

export interface FocusAreaRow {
  program: string;
  focusArea: string;
  /** Verbatim "Representative focus courses" cell. */
  focusCourses: string;
  /** Verbatim "Job roles" cell. */
  roles: string;
}

/**
 * Table F — the three B.S. focus areas, in the source document's order.
 *
 * These courses are *additional* to the ten B.S. rows in Table A: those ten
 * are the backbone every B.S. student completes whichever focus area they
 * pick. The page says so above the table.
 */
export const focusAreas: FocusAreaRow[] = records('/src/data/careers-focus-areas.csv').map((r) => ({
  program: r.program,
  focusArea: r.focus_area,
  focusCourses: r.focus_courses,
  roles: r.roles,
}));

/* ============================================================
   Demand side — Tables C, D and E.

   Tables A and B answer "this course teaches X, which leads to role Y, which
   pays Z". These three answer the question that leaves open: did employers
   actually ask for X? Same Lightcast report, same vintage as Table B
   (Q1 2026 Data Set, CIP 30.7102, United States, Master's-degree filter),
   pages 8-12.

   EDIT THE CSVs, NOT THIS FILE, NOT THE PAGE.
     careers-skills.csv         Table C — skills and tools named in postings
     careers-qualifications.csv Table D — qualifications requested
     careers-job-titles.csv     Table E — top posted job titles

   Percentages in Table C are the report's own, taken against the 32,539
   unique postings, and are stored verbatim rather than recomputed.
   ============================================================ */

/** Unique postings behind every Table C percentage. Report p7. */
export const UNIQUE_POSTINGS = '32,539';
/** Total postings for the same selection and window. Report p7. */
export const TOTAL_POSTINGS = '73,184';

/** Thousands separators for the raw integers the new CSVs carry. */
function withCommas(n: number): string {
  return n.toLocaleString('en-US');
}

export interface SkillRow {
  /** `Specialized`, `Software` or `Common` — the Table C filter dimension. */
  category: string;
  skill: string;
  /** Raw count, for sorting. */
  postings: number;
  /** `postings` with thousands separators. */
  postingsLabel: string;
  /** Verbatim, e.g. "41%". */
  pct: string;
  /** Digits of `pct`, for sorting. */
  pctValue: number;
  /** Verbatim, e.g. "+25.8%". */
  projectedGrowth: string;
  /** Verbatim, e.g. "Rapidly Growing". */
  growthVsMarket: string;
}

/**
 * Table C, in report order: Specialized, then Software, then Common, each
 * already descending by postings. That order is the page's "unsorted" state.
 *
 * SQL, Python and R are in the report's specialized-skills list AND its
 * software list, with identical postings, percentages and growth. They are
 * here once, under Software, because they are tools. Nothing was dropped —
 * the page's source line says this out loud.
 */
export const skills: SkillRow[] = records('/src/data/careers-skills.csv').map((r) => ({
  category: r.category,
  skill: r.skill,
  postings: Number(r.postings) || 0,
  postingsLabel: withCommas(Number(r.postings) || 0),
  pct: r.pct_of_postings,
  pctValue: Number(r.pct_of_postings.replace(/[^0-9.]/g, '')) || 0,
  projectedGrowth: r.projected_growth,
  growthVsMarket: r.growth_vs_market,
}));

/** Distinct Table C categories, in the order the CSV introduces them. */
export const skillCategories: string[] = [...new Set(skills.map((s) => s.category))];

export interface QualificationRow {
  qualification: string;
  postings: number;
  postingsLabel: string;
}

/**
 * Table D, postings descending. All ten rows the report lists, uncurated:
 * four are security clearances and one is a driver's license, which say
 * something about who is hiring in this occupation set rather than about the
 * curriculum. The page says so instead of deleting them — the same treatment
 * "Mathematical Science Occupations, All Other" already gets in Table B.
 */
export const qualifications: QualificationRow[] = records(
  '/src/data/careers-qualifications.csv',
)
  .map((r) => ({
    qualification: r.qualification,
    postings: Number(r.postings) || 0,
    postingsLabel: withCommas(Number(r.postings) || 0),
  }))
  .sort((a, b) => b.postings - a.postings);

export interface JobTitleRow {
  jobTitle: string;
  totalPostings: number;
  totalLabel: string;
  uniquePostings: number;
  uniqueLabel: string;
  /** Verbatim, e.g. "2 : 1". */
  postingIntensity: string;
  /** Raw day count, rendered with its unit on the page. */
  medianPostingDays: number;
}

/**
 * Table E, unique postings descending — the report's own ordering.
 *
 * Its job here is narrow: Data Analysts, Business Analysts and Business
 * Systems Analysts are role names Table A uses that have no Lightcast
 * occupation row, so Table B cannot price them. This table shows employers
 * posting for them by name. "Home Shopping Personal Shoppers" is classifier
 * noise and stays in for the same reason the clearances do.
 */
export const jobTitles: JobTitleRow[] = records('/src/data/careers-job-titles.csv')
  .map((r) => ({
    jobTitle: r.job_title,
    totalPostings: Number(r.total_postings) || 0,
    totalLabel: withCommas(Number(r.total_postings) || 0),
    uniquePostings: Number(r.unique_postings) || 0,
    uniqueLabel: withCommas(Number(r.unique_postings) || 0),
    postingIntensity: r.posting_intensity,
    medianPostingDays: Number(r.median_posting_days) || 0,
  }))
  .sort((a, b) => b.uniquePostings - a.uniquePostings);
