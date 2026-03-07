from app.extensions import db
from app.common.exceptions import ValidationError
from app.models import Shop
from .dto import CreateShopDTO, ShippingSetupDTO

class SellerService:

    @staticmethod
    def _validate_step_1(dto: CreateShopDTO):
        if not dto.name or len(dto.name.strip()) < 3:
            raise ValidationError("Tên shop tối thiểu 3 ký tự")
        if not dto.pickup_address or len(dto.pickup_address.strip()) < 10:
            raise ValidationError("Địa chỉ lấy hàng không hợp lệ")
        if not dto.email or "@" not in dto.email:
            raise ValidationError("Email liên hệ không hợp lệ")
        if not dto.phone or len(dto.phone.strip()) < 9:
            raise ValidationError("Số điện thoại liên hệ không hợp lệ")

    @staticmethod
    def register_shop(user, dto: CreateShopDTO):
        SellerService._validate_step_1(dto)

        existing_shop = Shop.query.filter_by(owner_id=user.id).first()
        if existing_shop:
            raise ValidationError("Bạn đã có shop, không thể tạo thêm")

        shop = Shop(
            owner_id=user.id,
            name=dto.name.strip(),
            pickup_address=dto.pickup_address.strip(),
            contact_email=dto.email.strip().lower(),
            contact_phone=dto.phone.strip(),
            onboarding_step=2,
        )

        db.session.add(shop)
        user.is_seller = True
        db.session.commit()

        return shop

    @staticmethod
    def setup_shipping(shop: Shop, dto: ShippingSetupDTO):
        if not any([
            dto.fast,
            dto.same_day,
            dto.express,
            dto.self_delivery,
            dto.pickup_point,
            dto.bulky,
        ]):
            raise ValidationError("Vui lòng bật ít nhất một hình thức vận chuyển")

        shop.shipping_fast = dto.fast
        shop.shipping_same_day = dto.same_day
        shop.shipping_express = dto.express
        shop.shipping_self_delivery = dto.self_delivery
        shop.shipping_pickup_point = dto.pickup_point
        shop.shipping_bulky = dto.bulky

        shop.shipping_configured = True
        shop.onboarding_step = 2
        shop.onboarding_completed = True
        db.session.commit()

        return shop
