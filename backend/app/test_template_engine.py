from template_engine.mapper import TemplateMapper
from template_engine.validator import TemplateValidator
from template_engine.generator import TemplateGenerator


def main():

    vm_inventory = [
        {
            "vm_name": "prod-web-01",
            "os": "Ubuntu Linux 22.04 (64-bit)",
            "ip": "10.0.0.15, fe80::1"
        },
        {
            "vm_name": "prod-db-01",
            "os": "Windows Server 2019",
            "ip": "10.0.0.20"
        },
        {
            "vm_name": "legacy-app",
            "os": "CentOS 7",
            "ip": None
        },
        {
            "vm_name": "dup-ip-server",
            "os": "RHEL 8.6",
            "ip": "10.0.0.20"
        },
        {
            "vm_name": "mystery-box",
            "os": "Solaris 10",
            "ip": "10.0.0.50"
        }
    ]

    mapper = TemplateMapper(
        account_id="123456789012",
        region="ap-south-1"
    )

    validator = TemplateValidator()
    generator = TemplateGenerator()

    mapped_records = []
    mapping_failures = []

    # ✅ MAP
    for vm in vm_inventory:
        try:
            mapped = mapper.map_record(vm)
            mapped_records.append(mapped)

        except Exception as e:
            vm["mapping_error"] = str(e)
            mapping_failures.append(vm)

    # ✅ VALIDATE
    ready, failed = validator.validate(mapped_records)

    # ✅ GENERATE CSV (ONLY READY RECORDS)
    generator.write_ready_csv(
        ready,
        output_path="mgn_ready.csv"
    )

    # -----------------------------
    # OUTPUT
    # -----------------------------

    print("\n✅ CSV GENERATED: mgn_ready.csv")

    print("\n✅ READY FOR IMPORT")
    for r in ready:
        print(r)

    print("\n❌ VALIDATION FAILURES")
    for f in failed:
        print(f)

    print("\n🔥 MAPPING FAILURES")
    for m in mapping_failures:
        print(m)


if __name__ == "__main__":
    main()
