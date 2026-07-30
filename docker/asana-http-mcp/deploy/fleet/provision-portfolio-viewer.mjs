const [memberGid, memberEmail] = process.argv.slice(2);
if (!memberGid || !memberEmail) {
  throw new Error(
    "Usage: provision-portfolio-viewer.mjs <member-gid> <member-email>",
  );
}

const token = process.env.ASANA_ACCESS_TOKEN;
if (!token) throw new Error("ASANA_ACCESS_TOKEN is missing");

const portfolios = [
  ["1209572726213901", "Directories"],
  ["1201894756128258", "GHL Growth Garage"],
  ["1198914117627792", "Test Portfolio"],
  ["1201922841183331", "Website Development"],
  ["1200401793845955", "ZedBiz Testing Websites"],
];

const base = "https://app.asana.com/api/1.0";
const headers = {
  Authorization: `Bearer ${token}`,
  "Content-Type": "application/json",
};
const results = [];

for (const [portfolioGid, portfolioName] of portfolios) {
  const query = new URL(`${base}/memberships`);
  query.searchParams.set("parent", portfolioGid);
  query.searchParams.set("member", memberGid);
  query.searchParams.set(
    "opt_fields",
    "gid,access_level,member.gid,parent.gid",
  );

  const existingResponse = await fetch(query, { headers });
  const existingBody = await existingResponse.json();
  if (!existingResponse.ok) throw new Error(JSON.stringify(existingBody));

  if (existingBody.data.length > 0) {
    const membership = existingBody.data[0];
    results.push({
      portfolio_gid: portfolioGid,
      portfolio_name: portfolioName,
      status: "preserved",
      access_level: membership.access_level,
      membership_gid: membership.gid,
    });
    continue;
  }

  const createResponse = await fetch(`${base}/memberships`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      data: {
        parent: portfolioGid,
        member: memberGid,
        access_level: "viewer",
      },
    }),
  });
  const createBody = await createResponse.json();
  if (!createResponse.ok) throw new Error(JSON.stringify(createBody));

  results.push({
    portfolio_gid: portfolioGid,
    portfolio_name: portfolioName,
    status: "created",
    access_level: createBody.data.access_level,
    membership_gid: createBody.data.gid,
  });
}

console.log(
  JSON.stringify({
    ok: true,
    member: { gid: memberGid, email: memberEmail },
    results,
  }),
);
