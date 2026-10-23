# Anonymization of the review package

The anonymous publication copy removes machine identity metadata and personal
workspace paths. The internal source copy and original six data volumes are
retained unchanged. Experimental numbers, labels, adjudications, captured
requests and responses, model outputs, and frozen lineage manifests are unchanged.
The fixed-hash D8 historical source is unchanged.

## Snapshot paths

In 1,531 source snapshots and 6,296 archive snapshot members, two
`data-vite-dev-id` values in the recorded `dom_html` contain CSS-source paths.
Only their personal workspace prefix was replaced with
`/subjects/cypress-realworld-app/`. The preserved suffixes are
`node_modules/react-calendar/dist/Calendar.css` and
`node_modules/react-virtualized/styles.css`.

The transformation operated on gzip-decoded JSON bytes. Apart from those two
HTML attribute values, the decoded JSON bytes are identical. Recorded URLs,
visible page text, form values, `action_id`, and `captured_at` are unchanged.
Modified gzip containers have an empty filename, zero container timestamp, and
OS byte 255; this does not alter the recorded capture timestamp. The 7,827
physical locations represent 1,654 unique modified snapshot byte sequences.

## Archive metadata

The six anonymous archives use neutral tar ownership fields (`uid=0`, `gid=0`,
empty owner and group names). Verified AppleDouble metadata entries and the
`LIBARCHIVE.xattr.com.apple.provenance` and
`SCHILY.xattr.com.apple.provenance` PAX attributes were removed. Remaining
member paths and order, types, file permissions, tar entry modification times,
and all 118 symbolic-link targets were preserved. Other file payloads are
byte-identical to their originals. The archive containers therefore have new
physical sizes and SHA-256 checksums.

## Physical checksums and historical provenance

Release checksums describe the actual distributed bytes. Use the current
release checksum list to check downloaded archives, and the source-file
checksum list where supplied to check extracted source files.

`artifact-relocation.json` serves a separate purpose: it maps the digest of an
identity-transformed file to the original digest and size pinned in the frozen
lineage. Its 393 existing mappings are retained; 1,654 snapshot mappings were
added after checking that no distributed digest identifies different original
bytes. `attested_sha256` and `attested_size` use these mappings for historical
lineage checks. Files absent from the map use their actual digest and size.
The page-state loader uses the same existing mapping mechanism; path
containment, JSON type checks, and recorded action identity checks are retained.
Historical provenance digests are not physical checksums of the anonymous files.

`anonymization-manifest.json` lists each changed relative path, its original and
anonymous digests and sizes, the number of changed attribute values, and the
six archive transformations. It intentionally omits the original personal path.

## Verification scope

Strict allowed-difference comparisons covered all transformed source and archive
members. Compatibility checks passed for 1,654 distinct snapshot pairs, 206 source
workflows, 642 frozen recording closures and their input lineage. Ten classes of
invalid input retain the original failure behavior; changing a non-identity field
does not obtain its original mapped digest or closure.

The isolated offline self-check passed all 24 comparisons and 29 internal commands.
All 67 supplied derived files match after normalizing only the exact local root
and top-level JSON generation timestamps. All 405 regenerated export catalogs and
test modules are byte-identical to the supplied versions. These checks use the
supplied frozen runs and review labels. The delivery verification report records
their scope and results.
