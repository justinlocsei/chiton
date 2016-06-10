import itertools

from chitonmark.benchmark import BaseBenchmark


class Benchmark(BaseBenchmark):

    fixtures = [
        'affiliate_item_factory',
        'affiliate_network_factory',
        'basic_factory',
        'brand_factory',
        'canonical_size_factory',
        'color_factory',
        'formality_factory',
        'garment_factory',
        'pipeline_profile_factory',
        'product_image_factory',
        'propriety_factory',
        'standard_size_factory',
        'stock_record_factory',
        'style_factory'
    ]

    def resolve_imports(self):
        from chiton.core.queries import prime_cached_queries
        from chiton.closet.data import CARE_CHOICES, EMPHASIS_CHOICES, PANT_RISE_CHOICES
        from chiton.runway.data import PROPRIETY_IMPORTANCE_CHOICES
        from chiton.wintour.data import EXPECTATION_FREQUENCY_CHOICES
        from chiton.wintour.matching import make_recommendations
        from chiton.wintour.pipelines.core import CorePipeline

        return {
            'CARE_CHOICES': CARE_CHOICES,
            'CorePipeline': CorePipeline,
            'EMPHASIS_CHOICES': EMPHASIS_CHOICES,
            'EXPECTATION_FREQUENCY_CHOICES': EXPECTATION_FREQUENCY_CHOICES,
            'make_recommendations': make_recommendations,
            'PANT_RISE_CHOICES': PANT_RISE_CHOICES,
            'prime_cached_queries': prime_cached_queries,
            'PROPRIETY_IMPORTANCE_CHOICES': PROPRIETY_IMPORTANCE_CHOICES
        }

    def pre_run(self, fixtures):

        # Create a pool of colors
        self.log('Creating colors')
        colors = [fixtures['color_factory']() for i in range(0, 3)]
        color_cycle = itertools.cycle(colors)

        # Create a pool of sizes
        self.log('Creating sizes')
        standard_sizes = []
        for size in range(0, 24, 4):
            canonical_size = fixtures['canonical_size_factory'](range_lower=size, range_upper=size + 2)
            for i in range(0, 4):
                variants = [False] * 4
                variants[i] = True
                standard_sizes.append(fixtures['standard_size_factory'](
                    canonical=canonical_size,
                    is_petite=variants[0],
                    is_plus_sized=variants[1],
                    is_regular=variants[2],
                    is_tall=variants[3]
                ))

        # Create a pool of formalities
        self.log('Creating formalities')
        formalities = [fixtures['formality_factory']() for i in range(0, 6)]
        formality_cycle = len(formalities) - 2

        # Create a pool of basics
        self.log('Creating basics')
        basics = []
        proprieties = self.imports['PROPRIETY_IMPORTANCE_CHOICES']
        for i in range(0, 20):
            basic = fixtures['basic_factory'](
                primary_color=next(color_cycle),
                budget_end=i * 5,
                luxury_start=i * 10
            )

            for j, formality in enumerate(formalities):
                fixtures['propriety_factory'](
                    basic=basic,
                    formality=formality,
                    importance=proprieties[(i + j) % (len(proprieties) - 1)][0]
                )

            basics.append(basic)
        basic_cycle = itertools.cycle(basics)

        # Create a pool of styles
        self.log('Creating styles')
        styles = [fixtures['style_factory']() for i in range(0, 7)]
        style_cycle = len(styles) - 2

        # Create brands for each decade
        self.log('Creating brands')
        brands = []
        for age in range(20, 80, 10):
            brands.append(fixtures['brand_factory'](age_lower=age, age_upper=age + 10))
        brand_cycle = itertools.cycle(brands)

        # Create cycle metrics for garment data
        care_type_cycle = itertools.cycle(self.imports['CARE_CHOICES'])
        emphasis_cycle = itertools.cycle(self.imports['EMPHASIS_CHOICES'])
        pant_rise_cycle = itertools.cycle(self.imports['PANT_RISE_CHOICES'])

        # Create a pool of affiliate networks
        self.log('Creating affiliate networks')
        affiliate_networks = [fixtures['affiliate_network_factory']() for i in range(0, 2)]
        affiliate_cycle = len(affiliate_networks) - 1

        # Create a large pool of garments
        for i in range(0, 100):
            self.log('Creating garment %d' % (i + 1), update=True)
            emphasis = next(emphasis_cycle)[0]
            garment = fixtures['garment_factory'](
                brand=next(brand_cycle),
                basic=next(basic_cycle),
                formalities=formalities[i % formality_cycle:-1],
                shoulder_emphasis=emphasis,
                waist_emphasis=emphasis,
                hip_emphasis=emphasis,
                pant_rise=next(pant_rise_cycle)[0],
                care=next(care_type_cycle)[0],
                styles=styles[i % style_cycle:-1]
            )

            for network in affiliate_networks[i % affiliate_cycle:-1]:
                price = basic.budget_end if i % 2 else basic.luxury_start
                price = price * 0.5 + i * 2 if i % 3 else price * 1.5 + i * 0.5

                affiliate_item = fixtures['affiliate_item_factory'](
                    network=network,
                    garment=garment,
                    price=price,
                    image=fixtures['product_image_factory'](),
                    thumbnail=fixtures['product_image_factory']()
                )

                for standard_size in standard_sizes:
                    fixtures['stock_record_factory'](
                        item=affiliate_item,
                        size=standard_size,
                        is_available=bool(i % 2)
                    )

        # Create formality expectations for the profile
        self.log('\nCreating profile')
        frequencies = self.imports['EXPECTATION_FREQUENCY_CHOICES']
        frequency_cycle = len(frequencies) - 1
        profile_expectations = {}
        for i, formality in enumerate(formalities):
            profile_expectations[formality.slug] = frequencies[i % frequency_cycle][0]

        # Create a profile from which to generate recommendations
        self._profile = fixtures['pipeline_profile_factory'](
            age=35,
            avoid_care=[self.imports['CARE_CHOICES'][-1][0]],
            expectations=profile_expectations,
            sizes=[size.slug for i, size in enumerate(standard_sizes) if i % 3],
            styles=[style.slug for style in styles[-2:]]
        )

        # Prime all cached queries now that the database is populated
        self.imports['prime_cached_queries']()

    def run(self, fixtures):
        self.imports['make_recommendations'](self._profile, pipeline=self.imports['CorePipeline']())
