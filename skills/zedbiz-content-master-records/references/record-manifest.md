# Working Record Manifest

Create this internal manifest before mutations. Keep it in task working state or the assignment activity record; do not create another Notion database for it.

| Field | Required content |
|---|---|
| Source | Original page ID, URL, file, note, or research request |
| Destination Database | Exact subject-owning Content Master Database and live data source |
| Page-Type | Actual live Notion Page-Type: Brief, Biz-Plan, Research, Jack, Source, or another supported value |
| Allocator Page-Type | Page-Type sent to the Z-Code allocator; must exactly match the final Notion Page-Type |
| Name-Key | Normalized allocator identity |
| Descriptor | Short useful title descriptor without filler or repeated Name-Key words |
| Proposed Page-Name | Exact `[Name-Key]-[Page-Type]-[Descriptor]` title, 3-8 dash-separated words total |
| Core | Full Z-Knowledge Core |
| Lane | Full Knowledge Lane |
| Topic Identity | Core + Lane + Topic Identifier; never the six-digit number alone |
| Research Mode | None, Small-Bite, or Full Wiki Research |
| Existing Match | Candidate page and verified same-item/same-purpose decision |
| Request ID | Stable allocator request ID for this creation attempt |
| Z-Code Status | Not started, found, reserved, requires review, failed, or confirmed |
| Destination URL | Final Notion page URL |
| Wiki Requirement | Required for every Core Content Database record |
| Wiki Artifact | Exact corresponding Memory Wiki file path |
| Verification | Minimal Notion check, allocator confirmation, full QA, and Wiki lint state |

Plan all expected records first. Execute allocation, publishing, minimal verification, confirmation, and the mandatory Wiki mirror sequentially for one record before starting the next.

