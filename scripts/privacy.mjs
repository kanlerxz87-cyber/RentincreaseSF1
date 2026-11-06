import fs from 'node:fs';
import path from 'node:path';

export function loadLocalPrivateIdentifiers(root) {
  const file = path.join(root, 'private', 'intake.json');
  if (!fs.existsSync(file)) return [];
  const intake = JSON.parse(fs.readFileSync(file, 'utf8'));
  const identifiers = [];
  for (const unit of ['unit_1', 'unit_2']) {
    for (const event of Object.values(intake[unit] ?? {})) {
      if (event && typeof event === 'object' && Array.isArray(event.resident_initials)) identifiers.push(...event.resident_initials);
    }
  }
  return [...new Set(identifiers)];
}

export function privateIdentifierPatterns(identifiers) {
  return identifiers.flatMap(identifier => {
    const variants = new Set([identifier.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')]);
    // A compact reported identifier may also be written with spaces. Do not
    // compact spaced initials: doing so turns ordinary words such as "is"
    // into false positives and is not the reported identifier format.
    if (!/\s/.test(identifier)) variants.add([...identifier].map(c => c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('\\s*'));
    return [...variants].map(variant => new RegExp(`(?<![A-Za-z0-9])(?:${variant})(?![A-Za-z0-9])`, 'gi'));
  });
}

export function containsPrivateIdentifier(text, identifiers) {
  return privateIdentifierPatterns(identifiers).some(pattern => {
    pattern.lastIndex = 0;
    return pattern.test(text);
  });
}

export function assertNoSensitiveStructure(value, location = 'public data') {
  if (Array.isArray(value)) return value.forEach((item, index) => assertNoSensitiveStructure(item, `${location}[${index}]`));
  if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) {
      if (['resident_initials', 'alias_map', 'initials', 'ssn', 'street_address'].includes(key)) throw new Error(`Sensitive field at ${location}.${key}`);
      assertNoSensitiveStructure(child, `${location}.${key}`);
    }
  }
}
