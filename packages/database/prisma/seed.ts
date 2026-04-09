// prisma/seed.ts
// Seed script for development and testing data population

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding Evijnar database...');

  // ========================================================================
  // PRICE NORMALIZER: CPT ↔ ICD-10 ↔ UHI Mapping
  // ========================================================================

  const priceNormalizers = await prisma.priceNormalizer.createMany({
    data: [
      {
        cpt_code: '99213',
        cpt_description: 'Office visit, established patient, low complexity',
        icd10_code: 'Z90.0',
        icd10_description: 'Encounter for general adult medical examination',
        uhi_code: 'CON-0001',
        clinical_category: 'Consultation',
        complexity_score: 1,
        us_median_cost_usd: 120,
        validation_date: new Date('2026-04-01'),
      },
      {
        cpt_code: '27447',
        cpt_description: 'Total knee replacement with prosthesis',
        icd10_code: 'M17.11',
        icd10_description: 'Primary osteoarthritis, right knee',
        uhi_code: 'SURG-1001',
        clinical_category: 'Orthopedic Surgery',
        complexity_score: 8,
        us_median_cost_usd: 35000,
        validation_date: new Date('2026-04-01'),
      },
      {
        cpt_code: '70450',
        cpt_description: 'CT head/brain without contrast',
        icd10_code: 'R51.9',
        icd10_description: 'Unspecified headache',
        uhi_code: 'DIAG-0051',
        clinical_category: 'Diagnostic Imaging',
        complexity_score: 3,
        us_median_cost_usd: 800,
        validation_date: new Date('2026-04-01'),
      },
      {
        cpt_code: '99214',
        cpt_description: 'Office visit, established patient, moderate complexity',
        icd10_code: 'Z00.00',
        icd10_description: 'Encounter for general adult medical examination',
        uhi_code: 'CON-0002',
        clinical_category: 'Consultation',
        complexity_score: 2,
        us_median_cost_usd: 180,
        validation_date: new Date('2026-04-01'),
      },
      {
        cpt_code: '92004',
        cpt_description: 'Comprehensive eye and visual examination',
        icd10_code: 'Z01.00',
        icd10_description: 'Encounter for general adult medical examination',
        uhi_code: 'EYE-001',
        clinical_category: 'Ophthalmology',
        complexity_score: 2,
        us_median_cost_usd: 150,
        validation_date: new Date('2026-04-01'),
      },
    ],
    skipDuplicates: true,
  });

  console.log(`✅ Created ${priceNormalizers.count} price normalizers`);

  // ========================================================================
  // GLOBAL HOSPITALS: JCI/NABH Accredited Centers of Excellence
  // ========================================================================

  const hospitals = await prisma.globalHospital.createMany({
    data: [
      {
        name: 'Apollo Hospitals Delhi',
        jci_accredited: true,
        jci_certificate_url: 'https://example.com/apollo-jci.pdf',
        jci_expires_at: new Date('2028-12-31'),
        nabh_accredited: true,
        nabh_certificate_url: 'https://example.com/apollo-nabh.pdf',
        nabh_expires_at: new Date('2027-06-30'),
        country_code: 'IN',
        state_province: 'Delhi',
        city: 'New Delhi',
        latitude: 28.5355,
        longitude: 77.3910,
        postal_code: '110076',
        phone_primary: '+910114016024',
        email: 'admin@apollodelhi.com',
        website_url: 'https://www.apollohospitals.com',
        hospital_type: 'SPECIALTY_CENTER',
        price_data_verified_at: new Date('2026-03-15'),
        price_data_source: 'HOSPITAL_SELF_REPORT',
        avg_quality_score: 92,
        complication_rate: 2.1,
        readmission_rate: 1.8,
        patient_reviews_count: 3240,
      },
      {
        name: 'Fortis Healthcare Mumbai',
        jci_accredited: true,
        jci_certificate_url: 'https://example.com/fortis-jci.pdf',
        jci_expires_at: new Date('2029-03-15'),
        nabh_accredited: true,
        country_code: 'IN',
        state_province: 'Maharashtra',
        city: 'Mumbai',
        latitude: 19.0760,
        longitude: 72.8777,
        postal_code: '400043',
        phone_primary: '+919167997999',
        email: 'admin@fortismumbai.com',
        website_url: 'https://www.fortishealthcare.com',
        hospital_type: 'SPECIALTY_CENTER',
        price_data_verified_at: new Date('2026-03-20'),
        price_data_source: 'HOSPITAL_SELF_REPORT',
        avg_quality_score: 94,
        complication_rate: 1.9,
        readmission_rate: 1.5,
        patient_reviews_count: 5100,
      },
      {
        name: 'Mayo Clinic Rochester',
        jci_accredited: true,
        jci_certificate_url: 'https://example.com/mayo-jci.pdf',
        jci_expires_at: new Date('2030-01-20'),
        country_code: 'US',
        state_province: 'Minnesota',
        city: 'Rochester',
        latitude: 44.0121,
        longitude: -92.4652,
        postal_code: '55902',
        phone_primary: '+15074662000',
        email: 'international@mayo.edu',
        website_url: 'https://www.mayoclinic.org',
        hospital_type: 'SPECIALTY_CENTER',
        price_data_verified_at: new Date('2026-02-28'),
        price_data_source: 'HHS_TRANSPARENCY',
        avg_quality_score: 98,
        complication_rate: 0.8,
        readmission_rate: 0.5,
        patient_reviews_count: 12500,
      },
      {
        name: 'Bumrungrad International Bangkok',
        jci_accredited: true,
        jci_certificate_url: 'https://example.com/bumrungrad-jci.pdf',
        jci_expires_at: new Date('2028-06-15'),
        country_code: 'TH',
        state_province: 'Bangkok',
        city: 'Bangkok',
        latitude: 13.7563,
        longitude: 100.5018,
        postal_code: '10110',
        phone_primary: '+6627665000',
        email: 'international@bumrungrad.com',
        website_url: 'https://www.bumrungrad.com',
        hospital_type: 'SPECIALTY_CENTER',
        price_data_verified_at: new Date('2026-03-10'),
        price_data_source: 'HOSPITAL_SELF_REPORT',
        avg_quality_score: 91,
        complication_rate: 2.3,
        readmission_rate: 1.9,
        patient_reviews_count: 8700,
      },
      {
        name: 'Rural Clinic Network - Tier 2 Hub',
        country_code: 'IN',
        state_province: 'Madhya Pradesh',
        city: 'Indore',
        latitude: 22.7196,
        longitude: 75.8577,
        postal_code: '452001',
        phone_primary: '+917312708000',
        email: 'contact@ruralclinic.co.in',
        website_url: 'https://www.ruralclinic.co.in',
        hospital_type: 'GENERAL_HOSPITAL',
        price_data_verified_at: new Date('2026-03-25'),
        price_data_source: 'HOSPITAL_SELF_REPORT',
        avg_quality_score: 78,
        complication_rate: 4.5,
        readmission_rate: 3.2,
        patient_reviews_count: 540,
      },
    ],
    skipDuplicates: true,
  });

  console.log(`✅ Created ${hospitals.count} global hospitals`);

  // ========================================================================
  // DEPARTMENTS for each hospital
  // ========================================================================

  const departments = await prisma.department.createMany({
    data: [
      // Apollo Delhi
      { hospital_id: (await prisma.globalHospital.findFirst({ where: { name: 'Apollo Hospitals Delhi' } }))?.id || '', name: 'Orthopedic Surgery', specialization_code: 'ORTHO', head_name: 'Dr. Rajesh Kumar', phone: '+910114016024' },
      { hospital_id: (await prisma.globalHospital.findFirst({ where: { name: 'Apollo Hospitals Delhi' } }))?.id || '', name: 'Cardiology', specialization_code: 'CARD', head_name: 'Dr. Priya Sharma', phone: '+910114016025' },
      { hospital_id: (await prisma.globalHospital.findFirst({ where: { name: 'Apollo Hospitals Delhi' } }))?.id || '', name: 'Neurology', specialization_code: 'NEURO', head_name: 'Dr. Amit Singh', phone: '+910114016026' },
      // Fortis Mumbai
      { hospital_id: (await prisma.globalHospital.findFirst({ where: { name: 'Fortis Healthcare Mumbai' } }))?.id || '', name: 'General Surgery', specialization_code: 'GENE', head_name: 'Dr. Vikram Patel', phone: '+919167997999' },
      { hospital_id: (await prisma.globalHospital.findFirst({ where: { name: 'Fortis Healthcare Mumbai' } }))?.id || '', name: 'Oncology', specialization_code: 'ONCO', head_name: 'Dr. Meera Desai', phone: '+919167998000' },
    ],
    skipDuplicates: true,
  });

  console.log(`✅ Created ${departments.count} departments`);

  // ========================================================================
  // PROCEDURE PRICES: Hospital-specific pricing
  // ========================================================================

  const apolloDelhiId = (await prisma.globalHospital.findFirst({ where: { name: 'Apollo Hospitals Delhi' } }))?.id;
  const fortisId = (await prisma.globalHospital.findFirst({ where: { name: 'Fortis Healthcare Mumbai' } }))?.id;
  const mayoId = (await prisma.globalHospital.findFirst({ where: { name: 'Mayo Clinic Rochester' } }))?.id;

  // Get a normalizer to reference
  const kneeReplacement = await prisma.priceNormalizer.findFirst({ where: { cpt_code: '27447' } });

  if (kneeReplacement && apolloDelhiId && fortisId && mayoId) {
    const procedurePrices = await prisma.procedurePrice.createMany({
      data: [
        {
          hospital_id: apolloDelhiId,
          normalizer_id: kneeReplacement.id,
          base_price: 18500,
          facility_fee: 2500,
          anesthesia_fee: 1200,
          surgeon_fee: 8000,
          currency_code: 'INR',
          effective_date: new Date('2026-01-01'),
          expires_at: new Date('2027-12-31'),
          success_rate: 96.5,
          complication_rate: 2.1,
          verified_at: new Date('2026-03-15'),
          data_source: 'HOSPITAL_SELF_REPORT',
        },
        {
          hospital_id: fortisId,
          normalizer_id: kneeReplacement.id,
          base_price: 20000,
          facility_fee: 2800,
          anesthesia_fee: 1500,
          surgeon_fee: 8500,
          currency_code: 'INR',
          effective_date: new Date('2026-01-01'),
          expires_at: new Date('2027-12-31'),
          success_rate: 97.2,
          complication_rate: 1.9,
          verified_at: new Date('2026-03-20'),
          data_source: 'HOSPITAL_SELF_REPORT',
        },
        {
          hospital_id: mayoId,
          normalizer_id: kneeReplacement.id,
          base_price: 28500,
          facility_fee: 3500,
          anesthesia_fee: 2000,
          surgeon_fee: 12000,
          currency_code: 'USD',
          effective_date: new Date('2026-01-01'),
          expires_at: new Date('2027-12-31'),
          success_rate: 99.1,
          complication_rate: 0.8,
          verified_at: new Date('2026-02-28'),
          data_source: 'HHS_TRANSPARENCY',
        },
      ],
      skipDuplicates: true,
    });

    console.log(`✅ Created ${procedurePrices.count} procedure prices`);
  }

  console.log('🎉 Seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
